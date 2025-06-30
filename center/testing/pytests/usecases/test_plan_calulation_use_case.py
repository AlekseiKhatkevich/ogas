import pytest

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
    assert instance.product_id != 0
    assert instance.in_stock_at_consumer == os_cons.in_stock
    assert instance.in_stock_at_producer == os_prod.in_stock



