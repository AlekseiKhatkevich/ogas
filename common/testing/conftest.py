import pytest
from polyfactory.pytest_plugin import register_fixture

import common.testing.factories as factories
from common import settings as orig_settings
from common.resources.database.postgres import db as _db
from common.resources.database.postgres.database import Database

register_fixture(factories.CategoryFactory)


@pytest.fixture
def db():
    return _db


@pytest.fixture
def settings():
    return orig_settings


@pytest.fixture
def save_in_db(db):
    async def _inner(factory):
        factory.__async_session__ = db.async_sessionmaker()
        await factory.create_async()
    return _inner


@pytest.fixture(autouse=True)
def augment_postgres_db(monkeypatch):
    test_db = Database(url=orig_settings.POSTGRES_TEST_DSN.unicode_string())
    monkeypatch.setattr('common.resources.database.postgres.db', test_db)
