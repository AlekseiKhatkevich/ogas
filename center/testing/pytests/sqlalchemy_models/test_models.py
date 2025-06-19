import pytest
from sqlalchemy.exc import IntegrityError

from center.orm_models import CapabilityORM, OrganizationStockORM


async def test_capability_orm_positive(capability_in_db, capabilities_repo):
    assert await capabilities_repo.exists(capability_in_db.id)


async def test_capability_orm_negative_uniqueness(test_db, capability_in_db):
    instance = CapabilityORM(
        product_id=capability_in_db.product_id,
        organization_id=capability_in_db.organization_id,
        period=capability_in_db.period,
        role=capability_in_db.role,
    )
    with pytest.raises(IntegrityError):
        async with test_db.async_session as session:
            session.add(instance)
            await session.commit()


async def test_capability_orm_negative_check_c(capability_factory, save_in_db):
    with pytest.raises(IntegrityError, match='value_gt_0_check'):
        await save_in_db(capability_factory, value=-1)


async def test_organization_stock_orm_positive(organization_stock_in_db, organization_stock_repo):
    assert await organization_stock_repo.exists(
        where=(OrganizationStockORM.organization_id == organization_stock_in_db.organization_id) &
              (OrganizationStockORM.product_id == organization_stock_in_db.product_id)
    )


@pytest.mark.parametrize(
    ['in_stock', 'min_level', 'max_level', 'necessity', 'err_str'],
    (
        [-1, 1, 1000, 0, 'in_stock_positive',],
        [1, -1, 1000, 0, 'min_level_positive',],
        [10, 1, -1, 0, 'max_level_positive',],
        [10, 1, 1000, -1, 'necessity_level_positive',],
        # [10, 1001, 1000, 0, 'min_max_level',],
    )
)
async def test_organization_stock_orm_negative(
        in_stock,
        min_level,
        max_level,
        necessity,
        err_str,
        organization_stock_factory,
        save_in_db
):
    with pytest.raises(IntegrityError, match=err_str):
        await save_in_db(
            organization_stock_factory,
            in_stock=in_stock,
            min_level=min_level,
            max_level=max_level,
            necessity=necessity,
        )
