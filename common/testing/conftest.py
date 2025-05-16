import subprocess
from typing import AsyncGenerator, Generator, TYPE_CHECKING

import pytest
from _pytest.monkeypatch import MonkeyPatch
from sqlalchemy import text
from sqlalchemy.util import greenlet_spawn

from common import settings as orig_settings
from common.resources.database.postgres import db as _db
from common.resources.database.postgres.alchemy_related import Base
from common.resources.database.postgres.database import Database

if TYPE_CHECKING:
    from common.settings.general import GeneralSettings


@pytest.fixture(scope='session')
def monkeysession() -> Generator[MonkeyPatch]:
    mpatch = MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture
def db() -> Database:
    return _db


@pytest.fixture(scope='session')
def settings() -> 'GeneralSettings':
    return orig_settings


@pytest.fixture(autouse=True, scope='session')
def augment_postgres_db(monkeysession, settings) -> None:
    test_db = Database(url=orig_settings.POSTGRES_TEST_DSN.unicode_string())
    monkeysession.setattr('common.resources.database.postgres.db', test_db)
    monkeysession.setenv('POSTGRES_DSN', settings.POSTGRES_TEST_DSN.unicode_string())


@pytest.fixture(autouse=True)
async def truncate_db(db) -> AsyncGenerator[None]:
    yield
    table_names = [table.name for table in Base.metadata.sorted_tables]
    async with db.async_session as session:
        await session.execute(text(fr'TRUNCATE {', '.join(table_names)} CASCADE'))
        await session.commit()


@pytest.fixture(scope='session', autouse=True)
async def apply_alembic_migrations(augment_postgres_db) -> None:
    await greenlet_spawn(lambda: subprocess.Popen(['alembic', 'upgrade', 'head']).wait())
