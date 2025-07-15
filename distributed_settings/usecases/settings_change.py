from ravendb.changes.types import DocumentChange, DocumentChangeType

from common.usecases.common import AbstractUseCase
from distributed_settings.repositories.ravendb import SettingsRavenDBRepository
from typing import TYPE_CHECKING
from typing import TYPE_CHECKING

from ravendb.changes.types import DocumentChange, DocumentChangeType

from common.usecases.common import AbstractUseCase
from distributed_settings.repositories.ravendb import SettingsRavenDBRepository

if TYPE_CHECKING:
    from distributed_settings.repositories.ravendb.common import CommonRavenDBRepository
    from distributed_settings.serializers.settings_out import SettingsOut


# {'app': 'test', 'setting1': 0, '@metadata': {'@collection': 'settings', '@change-vector': 'A:8944-XLLKVHXsQUyEgQ1hZ9BRBw', '@id': 'settings/test', '@last-modified': '2025-07-14T13:28:18.0174209Z'}}


# noinspection PyCallingNonCallable
class UpsertProductUseCase(AbstractUseCase):
    _tracking_states = frozenset([DocumentChangeType.PUT, ])

    def __init__(self, repository: 'CommonRavenDBRepository' = SettingsRavenDBRepository):
        self.repository = repository()

    async def execute(self):
        pass

    def on_change(self, change: DocumentChange):
        if change.type_of_change in self._tracking_states:
            payload = self.load_settings(change.key)

    def on_startup(self):
        settings = self.load_whole_collection()

    def load_settings(self, key: str) -> 'SettingsOut':
        return self.repository.load(key)

    def load_whole_collection(self) -> tuple['SettingsOut']:
        return tuple(self.repository.query_collection())

