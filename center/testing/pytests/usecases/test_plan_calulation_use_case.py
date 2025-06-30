import pytest

from center.usecases.operative_data import PlanCalculationUseCase


@pytest.fixture(scope='module')
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

    saved_necessity = await necessity_repo



