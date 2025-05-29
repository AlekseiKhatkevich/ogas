import asyncio
from typing import Never

from faststream import FastStream
from faststream.kafka import KafkaBroker

from center.serializers import CapabilityIn
from center.usecases.capability import UpdateCapabilitiesUseCase
from common import settings
from common.faststream.filters import contentype_json

broker = KafkaBroker(settings.KAFKA_DSN)

app = FastStream(broker)


__all__ = (
    'broker',
    'app',
)


capability_out_publisher = broker.publisher('capability_out')


@broker.subscriber('capability_in', filter=contentype_json)
@capability_out_publisher
async def create_or_update_capability(capabilities: set[CapabilityIn]) -> dict:
    """
    Принимает данные о производительностях от компании и записывает их в БД.
    """
    use_case = UpdateCapabilitiesUseCase(capabilities)
    res = await use_case.execute()
    return {'created': res.cnt_created, 'updated': res.cnt_updated}


async def main() -> Never:
    await app.run()


if __name__ == '__main__':  #  дебаг запускать отсюда
    asyncio.run(main())
