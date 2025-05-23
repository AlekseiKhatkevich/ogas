import pytest

from center.enums import Period
from center.repositories.postgres import CapabilityPostgresRepository
from center.serializers import CapabilityIn

"""
Тесты относящиеся к CapabilityPostgresRepository.
"""


@pytest.fixture(scope='module')
def repo() -> CapabilityPostgresRepository:
    return CapabilityPostgresRepository()


@pytest.fixture
def capabilities_for_each_period(
        product_in_db,
        organization_in_db,
        capability_in_factory,
) -> set[CapabilityIn]:
    capabilities = set()
    for name, value in Period.__members__.items():
        capabilities.add(
            capability_in_factory.build(
                organization_name=organization_in_db.name,
                product_id=product_in_db.id,
                period=value,
            ))
    return capabilities


async def test_positive_insert_or_update_capabilities_only_insert(
        repo,
        capabilities_for_each_period,
):

    result = await repo.insert_or_update_capabilities(capabilities_for_each_period)

    assert not result.cnt_updated
    assert result.cnt_created == len(capabilities_for_each_period)

    assert await repo.exists(ids=result.ids)
