import pytest
from sqlalchemy.exc import IntegrityError


async def test_product_orm_positive(product_in_db, product_repo):
    assert await product_repo.exists(ids=[product_in_db.id])


async def test_product_orm_negative_unique(
        product_in_db,
        save_in_db_session,
        product_factory,
):
    instance = product_factory.build(
        name=product_in_db.name,
        unit=product_in_db.unit,
        standard=product_in_db.standard,
    )

    with pytest.raises(IntegrityError, match='(name, unit, standard_code)'):
        await save_in_db_session(instance)
