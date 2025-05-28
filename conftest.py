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
    'common.testing.fixtures.repositories',
    'common.testing.fixtures.faststream',
    'center.testing.fixtures.orm_models',
    'center.testing.fixtures.pydantic_models',
    'center.testing.fixtures.repositories',
]


@pytest.fixture
def save_in_db_batch[SQLALCHEMY_T: 'Base'](test_db: 'Database') ->\
        Callable[[SQLAlchemyFactory[SQLALCHEMY_T]], Awaitable[list[SQLALCHEMY_T]]]:
    async def _inner(factory: SQLAlchemyFactory[SQLALCHEMY_T], batch_size: int = 1, **kwargs) -> list[SQLALCHEMY_T]:
        # noinspection PyClassVar
        factory.__async_session__ = test_db.async_sessionmaker()
        return await factory.create_batch_async(size=batch_size, **kwargs)
    return _inner


@pytest.fixture
def save_in_db[SQLALCHEMY_T: 'Base'](test_db: 'Database', save_in_db_batch) ->\
        Callable[[SQLAlchemyFactory[SQLALCHEMY_T]], Awaitable[SQLALCHEMY_T]]:
    async def _inner(factory: SQLAlchemyFactory[SQLALCHEMY_T], **kwargs) -> SQLALCHEMY_T:
        # noinspection PyClassVar,PyArgumentList
        instances = await save_in_db_batch(factory, batch_size=1, **kwargs)
        return instances[0]
    return _inner


@pytest.fixture
def save_in_db_session[SQLALCHEMY_T: 'Base'](test_db: 'Database') ->\
        Callable[[SQLALCHEMY_T], Awaitable[SQLALCHEMY_T]]:
    async def inner(instance: SQLALCHEMY_T) -> Awaitable[SQLALCHEMY_T]:
        async with test_db.async_session as session:
            session.add(instance)
            await session.commit()
        return instance
    return inner



@pytest.fixture(scope='session')
def monkeysession() -> Generator[MonkeyPatch]:
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope='session')
def settings() -> 'GeneralSettings':
    return orig_settings


@pytest.fixture(scope='session')
def test_db() -> 'Database':
    from common.resources.database.postgres.database import Database
    return Database(url=orig_settings.POSTGRES_TEST_DSN.unicode_string())


@pytest.fixture(autouse=True, )
async def augment_postgres_db(monkeypatch, settings, test_db) -> None:
    monkeypatch.setattr('common.resources.database.postgres.db', test_db)
    monkeypatch.setenv('POSTGRES_DSN', settings.POSTGRES_TEST_DSN.unicode_string())


@pytest.fixture(autouse=True)
async def augment_postgres_engine(test_db) -> AsyncGenerator[None]:
    test_db.connection = await test_db.engine.connect()
    transaction = await test_db.connection.begin()
    try:
        yield None
    finally:
        await transaction.rollback()
        await test_db.connection.close()


@pytest.fixture(autouse=True, scope='session')
async def truncate_db(test_db) -> None:
    from common.resources.database.postgres.alchemy_related import Base
    table_names = [table.name for table in Base.metadata.sorted_tables]
    async with test_db.async_session as session:
        await session.execute(text(fr'TRUNCATE {', '.join(table_names)} CASCADE'))
        await session.commit()


@pytest.fixture(scope='session', autouse=True)
async def apply_alembic_migrations() -> None:
    await greenlet_spawn(lambda: subprocess.Popen(['alembic', 'upgrade', 'head']).wait())


@pytest.fixture
def event_loop() -> Generator[AbstractEventLoop]:
    yield asyncio.get_event_loop()


def pytest_sessionfinish(session: 'Session', exitstatus: int) -> None:
    asyncio.get_event_loop().close()

