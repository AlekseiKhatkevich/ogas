import pytest

from center.enums import Period
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

    assert await repo.exists(ids=result.ids, where=model.updated_at == None)


async def test_positive_insert_or_update_capabilities_insert_plus_update(
        repo,
        capability_in_factory,
        capability_in_db,
        capabilities_for_each_period,
):
    """

    """
    capability_to_update = capability_in_factory.build(
        organization_name=capability_in_db.organization.name,
        product_id=capability_in_db.product_id,
        period=capability_in_db.period,
        value=capability_in_db.value + 1,
    )

    result = await repo.insert_or_update_capabilities({capability_to_update, *capabilities_for_each_period})

    assert await repo.exists(
        ids=result.ids_updated,
        where=model.updated_at.is_distinct_from(None) & (model.value == capability_in_db.value + 1),
    )
    assert await repo.exists(
        ids=result.ids_created,
        where=model.updated_at.is_not_distinct_from(None),
    )
    assert len(result.ids_updated) == 1
    assert len(result.ids_created) == len(capabilities_for_each_period)
# тест нет проблем с несколькоими одинкаовыми инстансами)хеш). Отсутсвие обновлениия при одинаковых value
