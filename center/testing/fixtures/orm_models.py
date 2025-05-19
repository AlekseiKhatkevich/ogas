import pytest
from polyfactory.pytest_plugin import register_fixture

from center.testing import factories

register_fixture(factories.OrganizationFactory)


@pytest.fixture
async def organization_in_db(save_in_db, organization_factory: factories.OrganizationFactory) -> 'OrganizationORM':
    organization_factory.build()
    return await save_in_db(organization_factory)
