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



def foo(x):
    print(x)
    print (x.__dict__)
    print(type(x))
    # {
    #     'type_of_change': < DocumentChangeType.PUT: 'Put' >, 'key': '19375b1f-0608-4bb3-8d64-98c8917a1c4e', 'collection_name': 'settings', 'change_vector': 'A:8930-XLLKVHXsQUyEgQ1hZ9BRBw'}

