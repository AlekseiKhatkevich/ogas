from typing import Never

from faststream import FastStream
from faststream.constants import ContentTypes
from faststream.kafka import KafkaBroker
import asyncio
from center.serializers import CapabilityIn
from common import settings

broker = KafkaBroker(settings.KAFKA_DSN)

app = FastStream(broker)


@broker.subscriber(
    'capability_in',
    filter=lambda msg: msg.content_type == ContentTypes.json,
)
async def create_or_update_capability(capability: list[CapabilityIn]):
    print(capability)


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  #  дебаг запускать отсюда
    asyncio.run(main())
