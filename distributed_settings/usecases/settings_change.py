from typing import Any

from ravendb.changes.types import DocumentChange, DocumentChangeType
from ravendb.tools.utils import DynamicStructure

from common.resources.database.ravendb.store import RavenDBDocumentStore, raven_db_store
from common.usecases.common import AbstractUseCase
DynamicStructure


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
        payload = {k: v for k, v in vars(settings).items() if k != self._metadata}
        return payload

