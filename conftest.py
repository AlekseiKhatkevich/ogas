import asyncio
import subprocess
from asyncio import AbstractEventLoop
from typing import AsyncGenerator, Awaitable, Callable, Generator, TYPE_CHECKING

import pytest
from _pytest.monkeypatch import MonkeyPatch
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from sqlalchemy import text
from sqlalchemy.util import greenlet_spawn

from common import settings as orig_settings

if TYPE_CHECKING:
    from common.resources.database.postgres.alchemy_related import Base
    from common.resources.database.postgres.database import Database
    from common.settings.general import GeneralSettings
    from _pytest.main import Session

pytest_plugins = [
    'common.testing.fixtures.orm_models',
    'center.testing.fixtures.orm_models',
    'center.testing.fixtures.pydantic_models',
]


@pytest.fixture
def db():
    from common.resources.database.postgres import db as _db
    return _db


@pytest.fixture
def save_in_db[SQLALCHEMY_T: 'Base'](db: 'Database') ->\
        Callable[[SQLAlchemyFactory[SQLALCHEMY_T]], Awaitable[SQLALCHEMY_T]]:
    async def _inner(factory: SQLAlchemyFactory[SQLALCHEMY_T]) -> SQLALCHEMY_T:
        # noinspection PyClassVar
        factory.__async_session__ = db.async_sessionmaker()
        return await factory.create_async()
    return _inner


@pytest.fixture(scope='session')
def monkeysession() -> Generator[MonkeyPatch]:
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope='session')
def settings() -> 'GeneralSettings':
    return orig_settings


@pytest.fixture(autouse=True, )
async def augment_postgres_db(monkeypatch, settings,) -> None:
    from common.resources.database.postgres.database import Database
    test_db = Database(url=orig_settings.POSTGRES_TEST_DSN.unicode_string())
    monkeypatch.setattr('common.resources.database.postgres.db', test_db)
    monkeypatch.setenv('POSTGRES_DSN', settings.POSTGRES_TEST_DSN.unicode_string())

    con = await test_db.engine.connect()

    test_db.connection = con
    trans = await test_db.connection.begin()

    yield None

    await trans.rollback()
    await con.close()


@pytest.fixture
async def truncate_db(db) -> AsyncGenerator[None]:
    from common.resources.database.postgres.alchemy_related import Base
    table_names = [table.name for table in Base.metadata.sorted_tables]
    async with db.async_session as session:
        await session.execute(text(fr'TRUNCATE {', '.join(table_names)} CASCADE'))
        await session.commit()

    yield


@pytest.fixture(scope='session', autouse=True)
async def apply_alembic_migrations() -> None:
    await greenlet_spawn(lambda: subprocess.Popen(['alembic', 'upgrade', 'head']).wait())


@pytest.fixture
def event_loop() -> Generator[AbstractEventLoop]:
    yield asyncio.get_event_loop()


def pytest_sessionfinish(session: 'Session', exitstatus: int) -> None:
    asyncio.get_event_loop().close()

