async def test_receive_organization_stock_data_positive(
        organization_stock_repo,
        organization_in_db,
        product_in_db,
        organization_stock_in_factory,
        kafka_broker,
        organization_token,
):
    stock = organization_stock_in_factory.build(product_id=product_in_db.id)
    await kafka_broker.publish(
        message=stock,
        topic='organization_stock_in',
        headers={
            'content-type': 'application/json',
            'organization_name': organization_in_db.name,
            'token': organization_token,
        },
    )

    assert await organization_stock_repo.count() == 1
