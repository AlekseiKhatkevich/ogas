from typing import Any

from ravendb.changes.types import DocumentChange, DocumentChangeType
from ravendb.tools.utils import DynamicStructure

from common.resources.database.ravendb.store import RavenDBDocumentStore, raven_db_store
from common.usecases.common import AbstractUseCase

# todo pydantic dataclass
# {'app': 'test', 'setting1': 0, '@metadata': {'@collection': 'settings', '@change-vector': 'A:8944-XLLKVHXsQUyEgQ1hZ9BRBw', '@id': 'settings/test', '@last-modified': '2025-07-14T13:28:18.0174209Z'}}


class UpsertProductUseCase(AbstractUseCase):
    _tracking_states = frozenset([DocumentChangeType.PUT, ])
    _metadata = '@metadata'

    def __init__(self, store: RavenDBDocumentStore = raven_db_store):
        self.store = store

    async def execute(self):
        pass

    def on_change(self, change: DocumentChange):
        if change.type_of_change in self._tracking_states:
            payload = self.load_settings(change.key)

    def load_settings(self, key: str) -> dict[str, Any]:
        with self.store.session as session:
            settings = session.load(key)
        return vars(settings)

