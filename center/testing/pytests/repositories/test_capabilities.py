import pytest

from center.enums import Period, Role
from center.orm_models import CapabilityORM
from center.repositories.postgres import CapabilityPostgresRepository
from center.serializers import CapabilityIn

"""
Тесты относящиеся к CapabilityPostgresRepository.
"""

model = CapabilityORM


@pytest.fixture(scope='module')
def repo() -> CapabilityPostgresRepository:
    return CapabilityPostgresRepository()


@pytest.fixture
def capabilities_for_each_period(product_in_db, organization_in_db, capability_in_factory) -> set[CapabilityIn]:
    capabilities = set()
    for value in Period.__members__.values():
        capabilities.add(
            capability_in_factory.build(
                organization_name=organization_in_db.name,
                product_id=product_in_db.id,
                period=value,
            ))
    return capabilities


async def test_positive_insert_or_update_capabilities_only_insert(repo, capabilities_for_each_period):
    """
    Позитивный тест метода insert_or_update_capabilities.
    При вызове метода данные о производительностях должны быть записаны в БД.
    """
    result = await repo.insert_or_update_capabilities(capabilities_for_each_period)

    assert not result.cnt_updated
    assert result.cnt_created == len(capabilities_for_each_period)

    assert await repo.count(where=model.updated_at == None) == len(result.ids)


async def test_positive_insert_or_update_capabilities_insert_plus_update(
        repo,
        capability_in_factory,
        capability_in_db,
        capabilities_for_each_period,
):
    capability_to_update = capability_in_factory.build(
        organization_name=capability_in_db.organization.name,
        product_id=capability_in_db.product_id,
        period=capability_in_db.period,
        role=capability_in_db.role,
        value=capability_in_db.value + 1,
    )

    result = await repo.insert_or_update_capabilities({capability_to_update, *capabilities_for_each_period})

    assert await repo.count(
        where=model.updated_at.is_distinct_from(None) &
              (model.value == capability_in_db.value + 1) &
              (model.id.in_(result.ids_updated)),
    ) == len(result.ids_updated)
    assert await repo.count(
        where=model.updated_at.is_not_distinct_from(None) & model.id.in_(result.ids_created)
    ) == len(result.ids_created)
    assert result.cnt_updated == 1
    assert result.cnt_created == len(capabilities_for_each_period)


async def test_no_update_with_same_value(capability_in_db, repo):
    capability_to_update = CapabilityIn(
        organization_name=capability_in_db.organization.name,
        product_id=capability_in_db.product_id,
        period=capability_in_db.period,
        value=capability_in_db.value,
        role=Role.PRODUCER,
    )

    result = await repo.insert_or_update_capabilities({capability_to_update, })

    assert not result.ids_updated
    assert not result.ids_updated

    assert await repo.exists(
        capability_in_db.id,
        where=model.updated_at.is_not_distinct_from(None),
    )
