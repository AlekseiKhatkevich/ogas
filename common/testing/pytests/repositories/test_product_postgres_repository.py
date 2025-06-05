from typing import TYPE_CHECKING

import pytest


from common.orm_models import CategoryORM, ProductCategoryM2MIntermediate


@pytest.fixture
async def categories_in_db(save_in_db_batch, category_factory) -> list['CategoryORM']:
    return await save_in_db_batch(category_factory, batch_size=3)


async def test_create_or_update_product_create_fresh(
        product_repo,
        standard_in_db,
        product_factory,
        categories_in_db,
):
    prod = product_factory.build(standard=standard_in_db)
    categories_ids = set(c.code for c in categories_in_db)

    instance = await product_repo.create_or_update_product(
        name=prod.name,
        unit=prod.unit,
        code=standard_in_db.code,
        categories=categories_ids,
    )
    await product_repo.refresh(instance, attribute_names=['categories', ])

    assert await product_repo.exists(instance.id)
    assert categories_ids == set(c.code for c in instance.categories)


async def test_create_or_update_product_update_existing(
        product_repo,
        product_in_db,
        categories_in_db,
        product_category_m2m_repo,
):
    new_categories_ids = set(c.code for c in categories_in_db)
    await product_repo.refresh(product_in_db, attribute_names=['categories', ])
    existing_categories = product_in_db.categories

    instance = await product_repo.create_or_update_product(
        name=product_in_db.name,
        unit=product_in_db.unit,
        code=product_in_db.standard_code,
        categories=new_categories_ids,
    )

    await product_repo.refresh(instance, attribute_names=['categories', ])

    assert await product_repo.exists(instance.id)
    assert new_categories_ids == set(c.code for c in instance.categories)
    assert not await product_category_m2m_repo.exists(
        where=(ProductCategoryM2MIntermediate.category_code.in_(c.code for c in existing_categories)))

