import contextlib
import dataclasses
from typing import AsyncGenerator, TYPE_CHECKING

import structlog
from aiokafka import AIOKafkaProducer

from common import settings
from common.resources.interfaces import HealthCheckable

if TYPE_CHECKING:
    pass
log = structlog.get_logger()

__all__ = (
    'KafkaBroker',
    'kafka_broker',
    'KafkaMessage',
)


@dataclasses.dataclass
class KafkaMessage:
    topic: str
    content: bytes

    def __str__(self):
        return f'Topic: {self.topic}, message: {self.content[:50]}'


class KafkaBroker(HealthCheckable):
    def __init__(self, bootstrap_server: str) -> None:
        self.bootstrap_server = bootstrap_server

    @property
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

    async def send(self, messages: list[KafkaMessage]) -> None:
        log.info(f'Kafka, got messages {messages}')
        async with self._get_running_producer() as producer:
            for message in messages:
                log.info(f'Kafka, sending message {message}')
                await producer.send_and_wait(message.topic, message.content)


kafka_broker = KafkaBroker(settings.KAFKA_DSN)
