import pytest
from polyfactory.pytest_plugin import register_fixture

import common.testing.factories as factories
from common.resources.database.postgres import db as _db

register_fixture(factories.CategoryFactory)


@pytest.fixture
def db():
    return _db


@pytest.fixture
async def async_session(db):
    async with db.async_session as session:
        yield session


@pytest.fixture
def save_in_db(db):
    async def _inner(factory):
        factory.__async_session__ = db.async_sessionmaker()
        await factory.create_async()
    return _inner

