import pytest
from sqlalchemy.exc import IntegrityError

from center.orm_models import CapabilityORM


async def test_capability_orm_positive(capability_in_db, capabilities_repo):
    assert await capabilities_repo.exists(ids=[capability_in_db.id])


async def test_capability_orm_negative_uniqueness(test_db, capability_in_db):
    instance = CapabilityORM(
        product_id=capability_in_db.product_id,
        organization_id=capability_in_db.organization_id,
        period=capability_in_db.period,
    )
    with pytest.raises(IntegrityError, match='uq_capability_product_id'):
        async with test_db.async_session as session:
            session.add(instance)
            await session.commit()

async def test_capability_orm_negative_check_c(capability_factory, save_in_db):
    capability = capability_factory.build(value=-1)
    await save_in_db(capability_factory)

