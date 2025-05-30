import pytest

from center.repositories.postgres import CapabilityPostgresRepository, OrganizationPostgresRepository


@pytest.fixture(scope='session')
def capabilities_repo() -> CapabilityPostgresRepository:
    return CapabilityPostgresRepository()


@pytest.fixture(scope='session')
def organization_repo() -> OrganizationPostgresRepository:
    return OrganizationPostgresRepository()
