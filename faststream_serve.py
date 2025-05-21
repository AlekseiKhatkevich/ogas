from faststream import FastStream
from faststream.kafka import KafkaBroker

from center.serializers import CapabilityIn
from common import settings

broker = KafkaBroker(settings.KAFKA_DSN)

app = FastStream(broker)


@broker.subscriber('capability_in')
async def create_or_update_capability(capability: list[CapabilityIn]):
    print(capability)


@broker.subscriber("test-topic")
async def handle(
    name: str,
    user_id: int,
):
    assert name == "John"
    assert user_id == 1
    print(name, '  ', user_id)

