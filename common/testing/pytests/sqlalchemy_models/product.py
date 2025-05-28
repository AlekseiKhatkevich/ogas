

async def test_product_orm_positive(product_in_db, product_repo):
    assert await product_repo.exists(ids=[product_in_db.id])