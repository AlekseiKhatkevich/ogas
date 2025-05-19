from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

from center.testing import factories

if TYPE_CHECKING:
    from center.orm_models import OrganizationORM, CapabilityORM

register_fixture(factories.OrganizationFactory)
register_fixture(factories.CapabilityFactory)


@pytest.fixture
async def organization_in_db(save_in_db, organization_factory: factories.OrganizationFactory) -> 'OrganizationORM':
    organization_factory.build()
    return await save_in_db(organization_factory)


@pytest.fixture
async def capability_in_db(save_in_db, capability_factory: factories.CapabilityFactory) -> 'CapabilityORM':
    capability_factory.build()
    return await save_in_db(capability_factory)

