import asyncio
from typing import Never

from faststream import Logger
from faststream.asgi import AsgiFastStream
from faststream.kafka import KafkaBroker
from faststream.kafka.opentelemetry import KafkaTelemetryMiddleware
from faststream.kafka.prometheus import KafkaPrometheusMiddleware
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from prometheus_client import CollectorRegistry, make_asgi_app

from center.faststream import capabilities
from common.faststream import product
from common import settings

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

app = AsgiFastStream(
    broker,
    asyncapi_path='/docs/asyncapi',
    asgi_routes=[
        ('/metrics', make_asgi_app(registry)),  # для prometheus
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


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  # дебаг запускать отсюда
    # noinspection PyUnreachableCode
    asyncio.run(main())
