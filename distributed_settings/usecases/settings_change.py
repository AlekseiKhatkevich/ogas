from typing import TYPE_CHECKING

import structlog

from ravendb.changes.types import DocumentChange, DocumentChangeType

from common import settings
from common.resources.database.kafka import KafkaBroker, KafkaMessage, kafka_broker
from common.usecases.common import AbstractUseCase
from distributed_settings.repositories.ravendb import SettingsRavenDBRepository

if TYPE_CHECKING:
    from distributed_settings.repositories.ravendb.common import CommonRavenDBRepository
    from distributed_settings.serializers.settings_out import SettingsSerializer

log = structlog.get_logger()


# noinspection PyCallingNonCallable
class DistributedSettingsHandlingUseCase(AbstractUseCase):
    _tracking_states = frozenset([DocumentChangeType.PUT, ])

    def __init__(self,
                 repository: 'CommonRavenDBRepository' = SettingsRavenDBRepository,
                 _kafka_broker: KafkaBroker = kafka_broker
                 ):
        self.repository = repository()
        self._kafka_broker = _kafka_broker

    async def execute(self) -> None:
        self.track_changes()
        await self.on_startup()

    @staticmethod
    def _construct_topic(app: str) -> str:
        return f'{settings.KAFKA_DISTRIBUTED_SETTINGS_TOPIC_PREFIX}_{app.lower()}'

    async def on_change(self, change: DocumentChange) -> None:
        log.info(f'Got change -- {change} from RavenDB')
        if change.type_of_change in self._tracking_states:
            settings_from_db = self.load_settings(change.key)
            log.info(f'Fetched settings entry -- {settings_from_db} from RavenDB.')
            topic = self._construct_topic(settings_from_db.app)
            await self.send_settings_to_kafka([KafkaMessage(topic, settings_from_db)])

    async def on_startup(self) -> None:
        settings_from_db = self.load_whole_collection()
        log.info(f'Startup::Fetched settings entry -- {settings_from_db} from RavenDB.')
        payload = [
            KafkaMessage(self._construct_topic(setting.app), setting)
            for setting in settings_from_db
        ]
        await self.send_settings_to_kafka(payload)

    def load_settings(self, key: str) -> 'SettingsSerializer':
        return self.repository.load(key)

    def load_whole_collection(self) -> tuple['SettingsSerializer']:
        return tuple(self.repository.query_collection())

    def track_changes(self) -> None:
        log.info('Start tracking changes on "settings" collection in ravenDB.')
        self.repository.track_changes(self.on_change)

    async def send_settings_to_kafka(self, messages: list[KafkaMessage]) -> None:
        log.info(f'Passing message to kafka, {messages}')
        await self._kafka_broker.send(messages)
