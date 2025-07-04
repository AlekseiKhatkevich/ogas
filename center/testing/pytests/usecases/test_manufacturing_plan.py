import pytest
from asyncstdlib import tee
from more_itertools import only

from center.enums import Role
from center.orm_models import PlanORM
from center.usecases.manufacturing_plan import ManufacturingPlanUseCase


@pytest.fixture
def use_case():
    return ManufacturingPlanUseCase()


@pytest.fixture
async def necessities_iter(
        necessity_data_in,
        capability_factory,
        save_in_db_batch,
):
    # noinspection PyArgumentList
    async def _generator():
        for capability in await save_in_db_batch(
                capability_factory,
                batch_size=5,
                role=Role.PRODUCER,
                product=necessity_data_in.product,
        ):
            yield capability

    return _generator()


@pytest.fixture
async def info_for_planing_iter(
        info_for_planning_dc_factory,
        necessity_data_in,
):
    # noinspection PyArgumentList
    async def _generator(**kwargs):
        for info in info_for_planning_dc_factory.batch(
                size=5,
                product_id=necessity_data_in.product_id,
                fact_time=necessity_data_in.created_at,
                product_unit=necessity_data_in.product.unit,
                to_produce=necessity_data_in.to_produce,
                **kwargs,
        ):
            yield info

    return _generator


async def test_calculate_plan_real_producers(
        use_case,
        necessity_data_in,
        info_for_planing_iter,
):
    product_id = necessity_data_in.product_id
    info_for_planing_iter_backup, info_for_planing_iter_curr = tee(info_for_planing_iter(), 2)

    plans = await use_case.calculate_plan(product_id, info_for_planing_iter_curr)

    assert len(plans) == 5
    for plan, info in zip(plans, [i async for i in info_for_planing_iter_backup]):
        assert isinstance(plan, PlanORM)
        assert plan.organization_id == info.producer_id
        assert plan.product_id == info.product_id
        assert plan.value == info.plan
        assert plan.fact_time == info.fact_time


async def test_calculate_plan_no_real_producers(
        use_case,
        necessity_data_in,
        info_for_planing_iter,
):
    product_id = necessity_data_in.product_id

    plans = await use_case.calculate_plan(product_id, info_for_planing_iter(is_warehouse=True))

    assert len(plans) == 1
    plan = only(plans)
    assert plan.organization_id is None
    assert plan.product_id == product_id
    assert plan.value == necessity_data_in.to_produce
    assert plan.fact_time == necessity_data_in.created_at


async def test_calculate_plan_execute(
        use_case,
        necessity_full_monty,
        plan_repo,
        kafka_broker,
):
    necessity_in_db, capabilities = necessity_full_monty

    await use_case.execute()

    assert await plan_repo.count() == len(capabilities)
# todo monkeypatch broker