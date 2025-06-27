from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

from center.testing import factories
from constants import ORGANIZATION_TEST_TOKEN

if TYPE_CHECKING:
    from center.orm_models import (
        OrganizationORM,
        CapabilityORM,
        OperativeDataORM,
        OrganizationStockORM,
        NecessityORM,
    )

register_fixture(factories.OrganizationFactory)
register_fixture(factories.CapabilityFactory)
register_fixture(factories.OperativeDataFactory)
register_fixture(factories.OrganizationStockFactory)
register_fixture(factories.NecessityFactory)


@pytest.fixture
async def necessity_data_in(save_in_db, necessity_factory: factories.NecessityFactory) -> 'NecessityORM':
    return await save_in_db(necessity_factory)


@pytest.fixture
async def operative_data_in(save_in_db, operative_data_factory: factories.OperativeDataFactory) -> 'OperativeDataORM':
    return await save_in_db(operative_data_factory)


@pytest.fixture
async def organization_in_db(save_in_db, organization_factory: factories.OrganizationFactory) -> 'OrganizationORM':
    return await save_in_db(organization_factory)


@pytest.fixture
async def capability_in_db(save_in_db, capability_factory: factories.CapabilityFactory) -> 'CapabilityORM':
    return await save_in_db(capability_factory)


@pytest.fixture
async def organization_stock_in_db(
        save_in_db,
        organization_stock_factory: factories.OrganizationStockFactory,
) -> 'OrganizationStockORM':
    return await save_in_db(organization_stock_factory)


@pytest.fixture(scope='session')
def organization_token() -> str:
    return ORGANIZATION_TEST_TOKEN
