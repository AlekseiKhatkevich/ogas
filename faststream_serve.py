import asyncio
from typing import Never

from faststream import FastStream
from faststream.constants import ContentTypes
from faststream.kafka import KafkaBroker

from center.serializers import CapabilityIn
from center.usecases.capability import UpdateCapabilitiesUseCase
from common import settings

broker = KafkaBroker(settings.KAFKA_DSN)

app = FastStream(broker)


async def get_broker[T:KafkaBroker](_broker) -> [T]:
    await _broker.connect()
    return _broker


@broker.subscriber(
    'capability_in',
    filter=lambda msg: msg.content_type == ContentTypes.json,
)
async def create_or_update_capability(capabilities: set[CapabilityIn]):
    """
    Принимает данные о производительностях от компании и записывает их в БД.
    """
    use_case = UpdateCapabilitiesUseCase(capabilities)
    cnt_created, cnt_updated = await use_case.execute()
    return cnt_created, cnt_updated


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  #  дебаг запускать отсюда
    asyncio.run(main())
