import asyncio
from typing import Never

from faststream import FastStream
from faststream.kafka import KafkaBroker

from center.faststream import capabilities
from common import settings

broker = KafkaBroker(settings.KAFKA_DSN)
broker.include_router(capabilities.router)

app = FastStream(broker)


__all__ = (
    'broker',
    'app',
)


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  #  дебаг запускать отсюда
    # noinspection PyUnreachableCode
    asyncio.run(main())
