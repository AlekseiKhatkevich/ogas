import datetime
import math
import random
import statistics

import pytest
import sqlalchemy as sa
import ulid

from center.enums import Period, Role
from center.orm_models import OperativeDataORM1HourView
from center.usecases.operative_data import PlanCalculationUseCase
from common.repositories.postgres import InfoForSchedule
from common.resources.database.postgres import db


async def test_insert_stock_minimal_data(
        organization_stock_repo,
        organization_in_db,
        product_in_db,
        organization_stock_in_factory,
):
    stock = organization_stock_in_factory.build(product_id=product_in_db.id)

    instance = await organization_stock_repo.insert_stock(stock, organization_in_db)

    assert instance.organization_id == organization_in_db.id
    assert instance.product_id == stock.product_id

    assert instance.min_level == 0
    assert instance.max_level == float('inf')
    assert instance.necessity is None

    assert instance.is_active
    assert instance.created_at
    assert instance.updated_at is None


@pytest.mark.parametrize(
    ['min_level', 'max_level', 'necessity', 'is_active'],
    [
        (1, float('inf'),  None, True,),
        (1, 1000,  None, True,),
        (1, 1000,  25, True,),
        (1, 1000,  25, False,),
    ]
)
async def test_insert_stock_more_data(
        min_level,
        max_level,
        necessity,
        is_active,
        organization_stock_repo,
        organization_in_db,
        product_in_db,
        organization_stock_in_factory,
):
    stock = organization_stock_in_factory.build(
        product_id=product_in_db.id,
        min_level=min_level,
        max_level=max_level,
        necessity=necessity,
        is_active=is_active,
    )

    instance = await organization_stock_repo.insert_stock(stock, organization_in_db)
    assert instance.min_level == min_level
    assert instance.max_level == max_level
    assert instance.necessity == necessity
    assert instance.is_active == is_active


async def test_insert_stock_update(
        organization_stock_repo,
        organization_stock_in_factory,
        organization_stock_in_db,
):
    stock = organization_stock_in_factory.build(
        product_id=organization_stock_in_db.product_id,
        min_level=30,
        max_level=999,
        necessity=100,
        is_active=False,
    )
    instance = await organization_stock_repo.insert_stock(stock, organization_stock_in_db.organization)

    assert await organization_stock_repo.count(is_active=False) == 1
    assert instance.min_level == 30
    assert instance.max_level == 999
    assert instance.necessity == 100
    assert not instance.is_active
    assert instance.updated_at is not None


async def create_operative_data_by_hour(
    product_id: ulid.ULID,
    organization_prod_id: ulid.ULID,
    organization_cons_id: ulid.ULID,
    od_avg_interval_hours: int = 24 * 21,
):
    now_bucket = datetime.datetime.now(tz=datetime.UTC).replace(minute=0, second=0, microsecond=0)
    data = []
    negative_diffs = []
    for minus_hours in range(od_avg_interval_hours):
        negative_diffs.append(negative_diff := random.uniform(0, 1000))

        common_data = {
                OperativeDataORM1HourView.hour_bucket: now_bucket - datetime.timedelta(hours=minus_hours),
                OperativeDataORM1HourView.product_id: product_id,
                OperativeDataORM1HourView.positive_diff: 0,
                OperativeDataORM1HourView.negative_diff: negative_diff
            }
        data.extend(
            [
                {**common_data, OperativeDataORM1HourView.organization_id: organization_prod_id},
                {**common_data, OperativeDataORM1HourView.organization_id: organization_cons_id}
            ]
        )

    stmt = sa.insert(OperativeDataORM1HourView).values(data)

    async with db.async_session as session:
        await session.execute(stmt)
        await session.commit()

    return statistics.mean(negative_diffs)


async def test_get_info_for_schedule_positive_base_case(
    organization_stock_repo,
    organization_stock_factory,
    organization_factory,
    capability_factory,
    product_in_db,
    save_in_db,
    save_in_db_batch,
):
    organization_prod, organization_cons = await save_in_db_batch(organization_factory, batch_size=2)
    os_prod = await save_in_db(organization_stock_factory, organization=organization_prod, product=product_in_db, is_active=True)
    os_cons = await save_in_db(organization_stock_factory, organization=organization_cons, product=product_in_db, is_active=True)
    cap_prod = await save_in_db(
        capability_factory,
        organization=organization_prod,
        product=product_in_db,
        period=Period.DAY,
        role=Role.PRODUCER,
    )
    cap_cons = await save_in_db(
        capability_factory,
        organization=organization_cons,
        product=product_in_db,
        period=Period.DAY,
        role=Role.CONSUMER,
    )
    avg_per_hour = await create_operative_data_by_hour(product_in_db.id, organization_prod.id, organization_cons.id)

    info_gen = organization_stock_repo.get_info_for_schedule()
    info = [info async for info in info_gen]

    for i in info:
        assert isinstance(i, InfoForSchedule)
        assert i.product_id == product_in_db.id

    producer, consumer = PlanCalculationUseCase.get_consumer_and_producer(info)

    assert producer.role == Role.PRODUCER
    assert consumer.role == Role.CONSUMER

    assert producer.in_stock == os_prod.in_stock
    assert consumer.in_stock == os_cons.in_stock

    assert math.isclose(producer.cons_per_hour, avg_per_hour, rel_tol=0.01)
    assert math.isclose(consumer.cons_per_hour, avg_per_hour, rel_tol=0.01)

    assert producer.necessity is None
    assert consumer.necessity is None

    assert producer.capability_per_interval == cap_prod.value
    assert consumer.capability_per_interval == cap_cons.value

    assert producer.min_level == os_prod.min_level
    assert consumer.min_level == os_cons.min_level

    assert producer.capability_interval == consumer.capability_interval == Period.DAY

    assert producer.avg_interval == consumer.avg_interval == datetime.timedelta(seconds=60 * 60 * 24 * 21)
