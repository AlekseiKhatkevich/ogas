import pytest


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
