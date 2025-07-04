import pytest

from center.enums import Period, Role


# noinspection PyArgumentList
@pytest.fixture
async def base_case_data_for_get_info_for_schedule(
        organization_stock_repo,
        organization_stock_factory,
        organization_factory,
        capability_factory,
        product_in_db,
        save_in_db,
        save_in_db_batch,
):
    organization_prod, organization_cons = await save_in_db_batch(organization_factory, batch_size=2)
    os_prod = await save_in_db(
        organization_stock_factory,
        organization=organization_prod,
        product=product_in_db,
        is_active=True,
        in_stock=0,
    )
    os_cons = await save_in_db(
        organization_stock_factory,
        organization=organization_cons,
        product=product_in_db,
        is_active=True,
        in_stock=0,
    )
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
    return product_in_db, organization_prod, organization_cons, os_prod, os_cons, cap_prod, cap_cons


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
