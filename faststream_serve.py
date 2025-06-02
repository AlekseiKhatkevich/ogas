import asyncio
from typing import Never

from faststream import FastStream, Logger
from faststream.kafka import KafkaBroker

from center.faststream import capabilities
from common import settings

__all__ = (
    'broker',
    'app',
)

broker = KafkaBroker(settings.KAFKA_DSN)
broker.include_router(capabilities.router)

app = FastStream(broker)


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


if __name__ == '__main__':  #  дебаг запускать отсюда
    # noinspection PyUnreachableCode
    asyncio.run(main())
