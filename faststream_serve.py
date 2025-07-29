import asyncio
import os
from typing import Callable, Never
import structlog
import logfire
from faststream import FastStream, Logger
from faststream.asgi import AsgiFastStream
from faststream.kafka import KafkaBroker
from faststream.kafka.opentelemetry import KafkaTelemetryMiddleware
from faststream.nats.opentelemetry import NatsTelemetryMiddleware
from faststream.kafka.prometheus import KafkaPrometheusMiddleware
from nats.js.api import StorageType
from prometheus_client import CollectorRegistry, make_asgi_app, multiprocess

from center.faststream import (
    capabilities,
    operative_data,
    organization,
    organization_stock,
    current_info,
    files,
)
from common import settings
from common.faststream import product, settings as settings_routes
from utils.logfire_related import logfire_configure

from faststream.nats import NatsBroker

__all__ = (
    'broker',
    'app',
    'nc_broker',
    'nc_app',
)

logfire_configure()
logfire.instrument_pydantic()

structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt='%Y-%m-%d %H:%M:%S', utc=True),
        logfire.StructlogProcessor(),
        structlog.dev.ConsoleRenderer(),
    ],
)

registry = CollectorRegistry()

broker = KafkaBroker(
    settings.KAFKA_DSN,
    middlewares=(
        # KafkaPrometheusMiddleware(registry=registry),
        KafkaTelemetryMiddleware(),
    )
)
broker.include_router(capabilities.router)
broker.include_router(product.router)
broker.include_router(organization.router)
broker.include_router(operative_data.router)
broker.include_router(organization_stock.router)
broker.include_router(settings_routes.router)

#  NATS HERE !!!
nc_broker = NatsBroker(
    settings.NATS_DSN.unicode_string(),
    middlewares=(NatsTelemetryMiddleware(),),
)
nc_broker.include_router(current_info.router)
nc_broker.include_router(files.router)
nc_app = FastStream(nc_broker)


def make_metrics_app() -> Callable:
    """Для работы в мультипроцессорном режиме."""
    path = settings.PROMETHEUS_MULTIPROC_DIR
    os.environ['PROMETHEUS_MULTIPROC_DIR'] = str(path)
    path.mkdir(parents=True, exist_ok=True)
    multiprocess.MultiProcessCollector(registry)
    return make_asgi_app(registry=registry)


metrics_app = logfire.instrument_asgi(make_metrics_app(), )

# noinspection PyTypeChecker
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


@app.on_startup
async def distributed_settings_handle(logger: Logger) -> None:
    from distributed_settings.usecases.settings_change import DistributedSettingsHandlingUseCase
    # use_case = DistributedSettingsHandlingUseCase()
    # logger.info('Starting distributed settings handling.')
    # await use_case.execute()
    # logger.info('Distributed settings have sent, subscription has applied.')


@app.after_startup
async def create_nats_object_storage() -> None:
    """Создаем бакет для получения файлов от организаций."""
    bucket = 'file_upload'
    await nc_broker.object_storage(
        bucket,
        description='File upload bucket.',
        storage=StorageType.FILE,
        ttl=60 * 60 * 24,
    )
    logfire.info('Created object storage after faststream app startup', bucket=bucket)


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  # дебаг запускать отсюда
    # noinspection PyUnreachableCode
    asyncio.run(main())
