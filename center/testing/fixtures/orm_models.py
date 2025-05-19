from typing import TYPE_CHECKING

import pytest
from polyfactory.pytest_plugin import register_fixture

from center.testing import factories

if TYPE_CHECKING:
    from center.orm_models import OrganizationORM

register_fixture(factories.OrganizationFactory)


@pytest.fixture
async def organization_in_db(save_in_db, organization_factory: factories.OrganizationFactory) -> 'OrganizationORM':
    organization_factory.build()
    return await save_in_db(organization_factory)
