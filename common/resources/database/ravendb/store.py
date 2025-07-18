import contextlib

from ravendb import DocumentStore

from common import settings


class RavenDBDocumentStore:
    def __init__(self,
                 url: str = settings.RAVEN_DB_SERVER_URL.unicode_string(),
                 db_name: str = settings.RAVEN_DB_DATABASE_NAME,
                 ) -> None:
        self.url = url
        self.db_name = db_name
        self._store = None

    @property
    def store(self) -> DocumentStore:
        if self._store is None:
            store = DocumentStore(self.url, self.db_name)
            store.initialize()
            self._store = store
        return self._store

    @property
    @contextlib.contextmanager
    def session(self):
        with self.store.open_session() as session:
            yield session


raven_db_store = RavenDBDocumentStore()
