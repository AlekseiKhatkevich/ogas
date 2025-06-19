import pytest

from center.repositories.postgres import (
    CapabilityPostgresRepository,
    OperativeDataPostgresRepository,
    OrganizationPostgresRepository,
    OrganizationStockPostgresRepository,
)


@pytest.fixture(scope='session')
def capabilities_repo() -> CapabilityPostgresRepository:
    return CapabilityPostgresRepository()


@pytest.fixture(scope='session')
def organization_repo() -> OrganizationPostgresRepository:
    return OrganizationPostgresRepository()


@pytest.fixture(scope='session')
def operative_data_repo() -> OperativeDataPostgresRepository:
    return OperativeDataPostgresRepository()


@pytest.fixture(scope='session')
def organization_stock_repo() -> OrganizationStockPostgresRepository:
    return OrganizationStockPostgresRepository()
