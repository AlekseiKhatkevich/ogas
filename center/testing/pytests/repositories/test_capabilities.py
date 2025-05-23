import pytest

from center.repositories.postgres import CapabilityPostgresRepository

"""
Тесты относящиеся к CapabilityPostgresRepository.
"""


@pytest.fixture
def repo() -> CapabilityPostgresRepository:
    return CapabilityPostgresRepository()


async def test_positive_insert_or_update_capabilities(
        product_in_db,
        organization_in_db,
        capability_in_factory,
        repo,
):
    capabilities = capability_in_factory.batch(
        size=10,
        organization_name=organization_in_db.name,
        product_id=product_in_db.id,
    )

    await repo.insert_or_update_capabilities(set(capabilities))
    1+1