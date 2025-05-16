from typing import Awaitable, Callable, TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

import common.testing.factories as factories


from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

if TYPE_CHECKING:
    from common.orm_models import CategoryORM, StandardORM, ProductORM
    from common.resources.database.postgres.alchemy_related import Base
    from common.resources.database.postgres.database import Database

register_fixture(factories.CategoryFactory)
register_fixture(factories.StandardFactory)
register_fixture(factories.ProductFactory)


@pytest.fixture
def save_in_db[SQLALCHEMY_T: 'Base'](db: 'Database') ->\
        Callable[[SQLAlchemyFactory[SQLALCHEMY_T]], Awaitable[SQLALCHEMY_T]]:
    async def _inner(factory: SQLAlchemyFactory[SQLALCHEMY_T]) -> SQLALCHEMY_T:
        # noinspection PyClassVar
        factory.__async_session__ = db.async_sessionmaker()
        return await factory.create_async()
    return _inner


@pytest.fixture
async def category_in_db(save_in_db, category_factory: factories.CategoryFactory) -> 'CategoryORM':
    category_factory.build()
    return await save_in_db(category_factory)


@pytest.fixture
async def standard_in_db(save_in_db, standard_factory: factories.StandardFactory) -> 'StandardORM':
    standard_factory.build()
    return await save_in_db(standard_factory)


@pytest.fixture
async def product_in_db(save_in_db, product_factory: factories.ProductFactory) -> 'ProductORM':
    product_factory.build()
    return await save_in_db(product_factory)
