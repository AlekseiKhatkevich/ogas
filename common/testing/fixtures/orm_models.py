from typing import Awaitable, Callable, TYPE_CHECKING, Type

import pytest
from polyfactory.pytest_plugin import register_fixture

import common.testing.factories as factories

if TYPE_CHECKING:
    from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
    from common.resources.database.postgres.database import Database

register_fixture(factories.CategoryFactory)


@pytest.fixture
def save_in_db(db: 'Database') -> Callable[[Type['SQLAlchemyFactory']], Awaitable[None]]:
    async def _inner(factory: Type['SQLAlchemyFactory']) -> None:
        factory.__async_session__ = db.async_sessionmaker()
        await factory.create_async()
    return _inner
