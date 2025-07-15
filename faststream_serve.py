import asyncio
import os
from typing import Callable, Never

from faststream import Logger
from faststream.asgi import AsgiFastStream
from faststream.kafka import KafkaBroker
from faststream.kafka.prometheus import KafkaPrometheusMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CollectorRegistry, make_asgi_app, multiprocess

from center.faststream import (capabilities, operative_data, organization, organization_stock)
from common import settings
from common.faststream import product

__all__ = (
    'broker',
    'app',
)

resource = Resource.create(attributes={'service.name': 'faststream'})
tracer_provider = TracerProvider(resource=resource)
trace.set_tracer_provider(tracer_provider)
exporter = OTLPSpanExporter(endpoint='http://localhost:4317')
processor = BatchSpanProcessor(exporter)
tracer_provider.add_span_processor(processor)

registry = CollectorRegistry()

broker = KafkaBroker(
    settings.KAFKA_DSN,
    middlewares=(
        KafkaPrometheusMiddleware(registry=registry),
    )
)
broker.include_router(capabilities.router)
broker.include_router(product.router)
broker.include_router(organization.router)
broker.include_router(operative_data.router)
broker.include_router(organization_stock.router)


def make_metrics_app() -> Callable:
    """Для работы в мультипроцессорном режиме."""
    path = settings.PROMETHEUS_MULTIPROC_DIR
    os.environ['PROMETHEUS_MULTIPROC_DIR'] = str(path)
    path.mkdir(parents=True, exist_ok=True)
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


metrics_app = make_metrics_app()

app = AsgiFastStream(
    broker,
    asyncapi_path='/docs/asyncapi',
    asgi_routes=[
        ('/metrics', metrics_app),
    ],
    title='OGAS',
    version='0.1.1',
)


@app.on_shutdown
def child_exit(logger: Logger) -> None:
    """Для работы Прометея в многопроцессорном режиме."""
    pid = os.getpid()
    multiprocess.mark_process_dead(pid)
    logger.info(f'Marking process with PID {pid} as dead.')


@app.on_shutdown
def empty_prometheus_multiproc_dir(logger: Logger) -> None:
    """Очистка папки с метриками прометеуса."""
    path = settings.PROMETHEUS_MULTIPROC_DIR
    for file in path.iterdir():
        if file.is_file():
            file.unlink(missing_ok=True)
            logger.info(f'Deleting file {file.name}.')


@app.on_startup
async def sanity_check(logger: Logger) -> None:
    from utils.common import get_all_subclasses
    from common.resources.interfaces import HealthCheckable
    from common.exceptions.external_services import ExternalServiceNotReady

    for subcls in get_all_subclasses(HealthCheckable):
        instance = subcls()
        is_ok = await instance.check_health()
        if not is_ok:
            raise ExternalServiceNotReady(
                f'Service "{instance.service_name}" is not ready yet. Abort!'
            )
        else:
            logger.info(
                f'Service "{instance.service_name}" is ready.'
            )


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  # дебаг запускать отсюда
    # noinspection PyUnreachableCode
    asyncio.run(main())
