from typing import TYPE_CHECKING

import structlog
from ravendb.changes.types import DocumentChange, DocumentChangeType

from common.usecases.common import AbstractUseCase
from distributed_settings.repositories.ravendb import SettingsRavenDBRepository

if TYPE_CHECKING:
    from distributed_settings.repositories.ravendb.common import CommonRavenDBRepository
    from distributed_settings.serializers.settings_out import SettingsOut

log = structlog.get_logger()


# noinspection PyCallingNonCallable
class UpsertProductUseCase(AbstractUseCase):
    _tracking_states = frozenset([DocumentChangeType.PUT, ])

    def __init__(self, repository: 'CommonRavenDBRepository' = SettingsRavenDBRepository):
        self.repository = repository()

    async def execute(self) -> None:
        self.on_startup()
        self.track_changes()

    def on_change(self, change: DocumentChange):
        log.info(f'Got change -- {change} from RavenDB')
        if change.type_of_change in self._tracking_states:
            settings = self.load_settings(change.key)
            log.info(f'Fetched settings entry -- {settings} from RavenDB.')

    def on_startup(self):
        settings = self.load_whole_collection()

    def load_settings(self, key: str) -> 'SettingsOut':
        return self.repository.load(key)

    def load_whole_collection(self) -> tuple['SettingsOut']:
        return tuple(self.repository.query_collection())

    def track_changes(self) -> None:
        self.repository.track_changes(self.on_change)
