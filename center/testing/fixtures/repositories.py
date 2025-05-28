import pytest

from center.repositories.postgres import CapabilityPostgresRepository


@pytest.fixture(scope='session')
def capabilities_repo() -> CapabilityPostgresRepository:
    return CapabilityPostgresRepository()
