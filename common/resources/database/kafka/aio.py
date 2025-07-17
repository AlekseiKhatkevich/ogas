import contextlib
import dataclasses
from typing import AsyncGenerator, Mapping, Sequence, TypeAlias

import pydantic_core
import structlog
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, TopicPartition
from pydantic import BaseModel, ValidationError

from common.resources.interfaces import HealthCheckable
from common.settings.kafka import KafkaSettings
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


def deserializer(value: bytes) -> 'SettingsSerializer':
    return SettingsSerializer.model_validate_json(value)


class KafkaBroker(HealthCheckable):
    def __init__(self, bootstrap_server: str) -> None:
        self.bootstrap_server = bootstrap_server
        self.topic = 'distset_ogas'

    @property
    async def producer(self) -> AIOKafkaProducer:
        return AIOKafkaProducer(
            bootstrap_servers=self.bootstrap_server,
            enable_idempotence=True,
            value_serializer=serializer,
            compression_type='gzip',
        )

    @property
    async def consumer(self) -> AIOKafkaConsumer:
        return AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_server,
            auto_offset_reset='latest',
            value_deserializer=deserializer,
            enable_auto_commit=False,
            request_timeout_ms=2 * 1000,
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

    @contextlib.asynccontextmanager
    async def _get_running_consumer(self) -> AsyncGenerator[AIOKafkaConsumer]:
        consumer = await self.consumer
        await consumer.start()
        yield consumer
        await consumer.stop()

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

    async def fetch_last_message(self) -> SettingsSerializer | None:
        log.info(f'Fetching a message in last offset in topic -- {self.topic}.')
        async with kafka_broker._get_running_consumer() as consumer:
            tp = TopicPartition(self.topic, 0)
            end_offset = await consumer.end_offsets([tp])
            last_message_offset = end_offset[tp] - 1
            if last_message_offset < 0:  # нет сообщений
                log.error(f'There is no any messages in topic {self.topic}')
                return None
            else:
                consumer.seek(tp, end_offset[tp] - 1)
                try:
                    record = await consumer.getone()
                except ValidationError as err:
                    log.error(f'Can not deserialize record. Exception -- {err.json()}')
                else:
                    return record.value
            return None


# noinspection PyTypeChecker, PyArgumentList
kafka_broker = KafkaBroker(KafkaSettings().KAFKA_DSN)
