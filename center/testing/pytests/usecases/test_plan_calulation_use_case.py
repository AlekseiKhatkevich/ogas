import pytest

from center.enums import Role
from center.usecases.operative_data import PlanCalculationUseCase


@pytest.fixture
def use_case() -> PlanCalculationUseCase:
    return PlanCalculationUseCase()


async def test_plan_calculation_use_case_positive_2_element_same_product(
        base_case_data_for_get_info_for_schedule,
        use_case,
        necessity_repo,
):
    (product_in_db,
     organization_prod,
     organization_cons,
     os_prod,
     os_cons,
     cap_prod,
     cap_cons
     ) = base_case_data_for_get_info_for_schedule

    await use_case.execute()

    assert await necessity_repo.count() == 1
    instance = use_case._last_created_instance
    assert instance.created_at is not None
    assert instance.product_id == product_in_db.id
    assert instance.to_produce != 0
    assert instance.in_stock_at_consumer == os_cons.in_stock
    assert instance.in_stock_at_producer == os_prod.in_stock


async def test_plan_calculation_use_case_positive_only_consumer(
        base_case_data_for_get_info_for_schedule,
        use_case,
        necessity_repo,
        capabilities_repo,
):
    (product_in_db,
     organization_prod,
     organization_cons,
     os_prod,
     os_cons,
     cap_prod,
     cap_cons
     ) = base_case_data_for_get_info_for_schedule
    cap_prod.role = Role.CONSUMER
    await capabilities_repo.add_all([cap_prod])

    await use_case.execute()

    assert await necessity_repo.count() == 1
    instance = use_case._last_created_instance
    assert instance.created_at is not None
    assert instance.in_stock_at_consumer == os_cons.in_stock + os_prod.in_stock
    assert instance.in_stock_at_producer == 0


async def test_plan_calculation_use_case_positive_only_producer(
        base_case_data_for_get_info_for_schedule,
        use_case,
        necessity_repo,
        capabilities_repo,
):
    (product_in_db,
     organization_prod,
     organization_cons,
     os_prod,
     os_cons,
     cap_prod,
     cap_cons
     ) = base_case_data_for_get_info_for_schedule
    cap_cons.role = Role.PRODUCER
    await capabilities_repo.add_all([cap_cons])

    await use_case.execute()

    with pytest.raises(AttributeError):
        use_case._last_created_instance

