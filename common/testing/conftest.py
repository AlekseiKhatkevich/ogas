import subprocess
from typing import AsyncGenerator, Awaitable, Callable, TYPE_CHECKING, Type

import pytest
from polyfactory.pytest_plugin import register_fixture
from sqlalchemy import text
from sqlalchemy.util import greenlet_spawn

import common.testing.factories as factories
from common import settings as orig_settings
from common.resources.database.postgres import db as _db
from common.resources.database.postgres.alchemy_related import Base
from common.resources.database.postgres.database import Database

if TYPE_CHECKING:
    from common.settings.general import GeneralSettings
    from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

register_fixture(factories.CategoryFactory)


@pytest.fixture(scope='session')
def monkeysession():
    from _pytest.monkeypatch import MonkeyPatch
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture
def db() -> Database:
    return _db


@pytest.fixture(scope='session')
def settings() -> 'GeneralSettings':
    return orig_settings


@pytest.fixture
def save_in_db(db: Database) -> Callable[[Type['SQLAlchemyFactory']], Awaitable[None]]:
    async def _inner(factory: Type['SQLAlchemyFactory']) -> None:
        factory.__async_session__ = db.async_sessionmaker()
        await factory.create_async()
    return _inner


@pytest.fixture(autouse=True, scope='session')
def augment_postgres_db(monkeysession, settings) -> None:
    test_db = Database(url=orig_settings.POSTGRES_TEST_DSN.unicode_string())
    monkeysession.setattr('common.resources.database.postgres.db', test_db)


@pytest.fixture(autouse=True)
async def truncate_db(db) -> AsyncGenerator[None]:
    yield
    table_names = [table.name for table in Base.metadata.sorted_tables]
    async with db.async_session as session:
        await session.execute(text(fr'TRUNCATE {', '.join(table_names)} CASCADE'))
        await session.commit()


@pytest.fixture(scope='session', autouse=True)
async def apply_alembic_migrations(augment_postgres_db, monkeysession, settings) -> None:
    monkeysession.setenv('POSTGRES_DSN', settings.POSTGRES_TEST_DSN.unicode_string())
    await greenlet_spawn(lambda: subprocess.Popen(['alembic', 'upgrade', 'head']).wait())
