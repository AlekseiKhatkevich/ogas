import contextlib
from typing import Any, AsyncGenerator, TYPE_CHECKING

from aiokafka import AIOKafkaProducer
from asyncstdlib.functools import cached_property

from common import settings
from common.resources.interfaces import HealthCheckable

if TYPE_CHECKING:
    pass


__all__ = (
    'KafkaBroker',
    'kafka_broker',
)


class KafkaBroker(HealthCheckable):
    def __init__(self, bootstrap_server: str) -> None:
        self.bootstrap_server = bootstrap_server

    @cached_property
    async def producer(self) -> AIOKafkaProducer:
        return AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_server,
            enable_idempotence=True,
        )

    async def service_name(self) -> str:
        return 'Kafka_on_distributed_settings'

    async def check_health(self) -> bool:
        return True

    @contextlib.asynccontextmanager
    async def _get_running_producer(self) -> AsyncGenerator[AIOKafkaProducer]:
        producer = await self.producer
        await producer.start()
        yield producer
        await producer.stop()

    async def send_one(self, topic: str, message: bytes) -> None:
        async with self._get_running_producer() as producer:
            await producer.send_and_wait(topic, message)


kafka_broker = KafkaBroker(settings.KAFKA_DSN)
