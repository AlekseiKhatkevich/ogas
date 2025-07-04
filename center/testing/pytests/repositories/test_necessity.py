import pytest

from center.enums import Role
from common.repositories.postgres import InfoForPlanning


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
    )
    capability_different_product = await save_in_db_batch(
        capability_factory,
        batch_size=1,
        role=Role.PRODUCER,
    )
    capability_same_product_but_consumer = await save_in_db_batch(
        capability_factory,
        batch_size=1,
        role=Role.CONSUMER,
        product=necessity_data_in.product,
    )
    return necessity_data_in, capabilities


async def test_get_necessities_for_planing(
        necessity_repo,
        necessity_full_monty,
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


