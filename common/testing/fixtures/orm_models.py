from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

import common.testing.factories as factories

if TYPE_CHECKING:
    from common.orm_models import CategoryORM, StandardORM, ProductORM

register_fixture(factories.CategoryFactory)
register_fixture(factories.StandardFactory)
register_fixture(factories.ProductFactory)


@pytest.fixture
async def category_in_db(save_in_db, category_factory: factories.CategoryFactory) -> 'CategoryORM':
    return await save_in_db(category_factory)


@pytest.fixture
async def standard_in_db(save_in_db, standard_factory: factories.StandardFactory) -> 'StandardORM':
    return await save_in_db(standard_factory)


@pytest.fixture
async def product_in_db(save_in_db, product_factory: factories.ProductFactory) -> 'ProductORM':
    return await save_in_db(product_factory)
