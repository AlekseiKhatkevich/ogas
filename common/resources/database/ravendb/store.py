import contextlib

import logfire
from ravendb import DocumentStore

from common import settings
from common.resources.interfaces import HealthCheckable


class RavenDBDocumentStore(HealthCheckable):
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
    @logfire.instrument('ravendb_session', allow_generator=True, record_return=True)
    def session(self):
        with self.store.open_session() as session:
            yield session

    async def check_health(self):
        # with self.session as session, contextlib.suppress(RuntimeError):
        #     session.load('test/huest')
        #     return True
        # return False
        return True

    @property
    def service_name(self) -> str:
        return 'RavenDB'


raven_db_store = RavenDBDocumentStore()
