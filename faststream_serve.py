import asyncio
import os
from typing import Callable, Never

from faststream import Context, ContextRepo, Logger
from faststream.asgi import AsgiFastStream
from faststream.kafka import KafkaBroker
from faststream.kafka.prometheus import KafkaPrometheusMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CollectorRegistry, make_asgi_app, start_http_server
from prometheus_client.multiprocess import MultiProcessCollector

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
        # KafkaTelemetryMiddleware(tracer_provider=tracer_provider),
    )
)
broker.include_router(capabilities.router)
broker.include_router(product.router)
broker.include_router(organization.router)
broker.include_router(operative_data.router)
broker.include_router(organization_stock.router)


def make_metrics_app() -> Callable:
    """
    https://prometheus.github.io/client_python/multiprocess/
    """
    path = settings.PROMETHEUS_MULTIPROC_DIR
    path.mkdir(parents=True, exist_ok=True)
    for file in path.iterdir():
        if file.is_file():
            file.unlink()
    os.environ['PROMETHEUS_MULTIPROC_DIR'] = str(path)
    registry = CollectorRegistry()
    MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


app = AsgiFastStream(
    broker,
    asyncapi_path='/docs/asyncapi',
    asgi_routes=[
        ('/metrics', make_asgi_app(registry)),  # для prometheus faststream
        # ('/metrics_else', make_metrics_app()),
    ],
    title='OGAS',
    version='0.1.1',
)


@app.on_startup
async def sanity_check(logger: Logger):
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


@app.on_startup
def start_prometheus_server(context: ContextRepo) -> None:
    server, t = start_http_server(
        settings.PROMETHEUS_HTTP_SERVER_PORT,
        'localhost',
    )
    context.set_global('promet_srv_pair', (server, t, ))


@app.on_shutdown
def stop_prometheus_server(promet_srv_pair: tuple = Context()) -> None:
    server, t = promet_srv_pair
    server.shutdown()
    t.join()


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  # дебаг запускать отсюда
    # noinspection PyUnreachableCode
    asyncio.run(main())
