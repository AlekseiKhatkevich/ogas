import pytest

from center.enums import Period, Role
from common.repositories.postgres import InfoForPlanning
from conftest import save_in_db


# noinspection PyArgumentList
@pytest.fixture
async def extra_capabilities(
        capability_factory,
        save_in_db,
        necessity_data_in,
):
    await save_in_db(
        capability_factory,
        role=Role.PRODUCER,
    )
    await save_in_db(
        capability_factory,
        role=Role.CONSUMER,
        product=necessity_data_in.product,
    )


# noinspection PyArgumentList
@pytest.fixture
async def necessity_full_monty(
        necessity_data_in,
        capability_factory,
        save_in_db_batch,
):
    capabilities = await save_in_db_batch(
        capability_factory,
        batch_size=2,
        role=Role.PRODUCER,
        product=necessity_data_in.product,
        period=Period.DAY,
    )

    return necessity_data_in, capabilities


# noinspection PyArgumentList
@pytest.fixture
async def capability_duplicate(
        necessity_full_monty,
        save_in_db,
        capability_factory,
        necessity_data_in,
):
    necessity_in_db, capabilities = necessity_full_monty
    cap_duplicate = await save_in_db(
        capability_factory,
        role=Role.PRODUCER,
        product=necessity_data_in.product,
        organization=capabilities[0].organization,
        period=Period.MONTH,
    )
    return cap_duplicate


# noinspection PyArgumentList
@pytest.fixture
async def necessity_only_warehouse(
        necessity_data_in,
        capability_factory,
        save_in_db,
):
    cap_prod = await save_in_db(
        capability_factory,
        role=Role.PRODUCER,
        product=necessity_data_in.product,
    )
    cap_cons = await save_in_db(
        capability_factory,
        role=Role.CONSUMER,
        product=necessity_data_in.product,
        organization=cap_prod.organization,
    )
    return cap_prod, cap_cons


async def test_get_necessities_for_planing(
        necessity_repo,
        necessity_full_monty,
        extra_capabilities,
):
    necessity_in_db, capabilities = necessity_full_monty
    cap_dict = {c.organization_id: c for c in capabilities}

    entries = [e async for e in necessity_repo.get_necessities_for_planing()]

    assert len(entries) == 2
    for e in entries:
        assert isinstance(e, InfoForPlanning)
        assert e.product_id == necessity_in_db.product_id
        assert e.to_produce == necessity_in_db.to_produce
        assert e.fact_time == necessity_in_db.created_at
        assert e.producer_id in cap_dict.keys()
        assert e.capability_interval == cap_dict[e.producer_id].period
        assert not e.is_warehouse
        assert e.product_unit == necessity_in_db.product.unit
        assert e.common_capacity_per_hour is None


async def test_get_necessities_for_planing_warehouse(
        necessity_only_warehouse,
        necessity_repo,
):
    entries = [e async for e in necessity_repo.get_necessities_for_planing()]

    assert len(entries) == 1
    entry = entries[0]
    assert entry.is_warehouse


async def test_test_get_necessities_for_planing_no_producer(
        necessity_data_in,
        necessity_repo,
):
    entries = [e async for e in necessity_repo.get_necessities_for_planing()]

    assert len(entries) == 1
    entry = entries[0]
    assert entry.producer_id is None


async def test_test_get_necessities_for_planing_no_duplicates_by_period(
        necessity_repo,
        necessity_full_monty,
        capability_duplicate,
):
    entries = [e async for e in necessity_repo.get_necessities_for_planing()]

    assert len(entries) == 2
    for e in entries:
        assert e.capability_interval == Period.DAY


@pytest.mark.parametrize(
    ('periods', 'expected',),
    [
        [(Period.HOUR, Period.DAY, Period.WEEK, Period.MONTH, Period.QUARTER, Period.YEAR), Period.DAY],
        [(Period.HOUR, Period.WEEK, Period.MONTH, Period.QUARTER, Period.YEAR), Period.WEEK],
        [(Period.HOUR, Period.MONTH, Period.QUARTER, Period.YEAR), Period.MONTH],
        [(Period.HOUR, Period.QUARTER, Period.YEAR), Period.QUARTER],
        [(Period.HOUR, Period.YEAR), Period.YEAR],
        [(Period.HOUR,), Period.HOUR],
    ]
)
async def test_test_get_necessities_for_planing_sorting(
        periods,
        expected,
        necessity_repo,
        save_in_db_session,
        capability_factory,
        necessity_data_in,
        organization_in_db,
):
    capabilities = []
    for p in periods:
        capabilities.append(
            capability_factory.build(
                role=Role.PRODUCER,
                product=necessity_data_in.product,
                organization=organization_in_db,
                period=p,
            )
        )
    await save_in_db_session(capabilities)

    entries = [e async for e in necessity_repo.get_necessities_for_planing()]

    assert len(entries) == 1
    entry = entries[0]
    assert entry.capability_interval == expected
