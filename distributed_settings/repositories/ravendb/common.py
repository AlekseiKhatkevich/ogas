from abc import ABC, abstractmethod

from typing import TYPE_CHECKING

from common.resources.database.ravendb.store import RavenDBDocumentStore, raven_db_store

if TYPE_CHECKING:
    from ravendb import DocumentQuery

__all__ = (
    'CommonRavenDBRepository',
)


class AbstractRavenDBRepository(ABC):
    @property
    @abstractmethod
    def _collection(self) -> str | None:
        pass

    @property
    @abstractmethod
    def _object_type(self) -> object:
        pass

    def __init__(self, store: RavenDBDocumentStore = raven_db_store, /, ) -> None:
        self.store = store


class CommonRavenDBRepository[OT](AbstractRavenDBRepository):
    _collection: str
    _object_type: OT = OT

    def load(self, key: str) -> OT:
        with self.store.session as session:
            return session.load(key, self._object_type)

    def query_collection(self) -> 'DocumentQuery[OT]':
        with self.store.session as session:
            return session.query_collection(self._collection, self._object_type)
