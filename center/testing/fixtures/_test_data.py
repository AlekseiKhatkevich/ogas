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
    )
    os_cons = await save_in_db(
        organization_stock_factory,
        organization=organization_cons,
        product=product_in_db,
        is_active=True,
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
