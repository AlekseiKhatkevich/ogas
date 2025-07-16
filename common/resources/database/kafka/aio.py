import contextlib
import dataclasses
from typing import Any, AsyncGenerator, Mapping, Sequence, TYPE_CHECKING, TypeAlias

import pydantic_core
import structlog
from aiokafka import AIOKafkaProducer
from pydantic import BaseModel

from common import settings
from common.resources.interfaces import HealthCheckable

if TYPE_CHECKING:
    from distributed_settings.serializers.settings_out import SettingsSerializer


log = structlog.get_logger()

JSON_ro: TypeAlias = Mapping[str, "JSON_ro"] | Sequence["JSON_ro"] | str | int | float | bool | None

__all__ = (
    'KafkaBroker',
    'kafka_broker',
    'KafkaMessage',
)


@dataclasses.dataclass
class KafkaMessage:
    topic: str
    content: 'SettingsSerializer'

    def __str__(self):
        return f'Topic: {self.topic}, message: {self.content}'


def serializer(value: JSON_ro | BaseModel | bytes) -> bytes:
    match value:
        case BaseModel():
            return value.model_dump_json().encode('utf-8')
        case bytes():
            return value
        case _:
            return pydantic_core.to_json(value)


class KafkaBroker(HealthCheckable):
    def __init__(self, bootstrap_server: str) -> None:
        self.bootstrap_server = bootstrap_server

    @property
    async def producer(self) -> AIOKafkaProducer:
        return AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_server,
            enable_idempotence=True,
            value_serializer=serializer,
            compression_type='gzip',
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
                await producer.send_and_wait(
                    message.topic,
                    message.content,
                    key=message.content.app.encode('utf-8'),
                )


kafka_broker = KafkaBroker(settings.KAFKA_DSN)
