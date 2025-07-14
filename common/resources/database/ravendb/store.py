from ravendb import DocumentStore

from common import settings


class DocumentStoreHolder:
    _store: DocumentStore = None

    @staticmethod
    def _create_document_store() -> DocumentStore:
        server_url = settings.RAVEN_DB_SERVER_URL.unicode_string()
        database_name = settings.RAVEN_DB_DATABASE_NAME

        document_store = DocumentStore([server_url], database_name)

        document_store.initialize()
        return document_store

    @classmethod
    def store(cls) -> DocumentStore:
        if cls._store is None:
            cls._store = cls._create_document_store()

        return cls._store
