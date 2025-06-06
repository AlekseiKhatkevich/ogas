async def test_create_or_update_product_handler_positive(
        standard_in_db,
        product_factory,
        kafka_broker,
        product_repo,
):
    product = product_factory.build(standard=standard_in_db)
    model = product_repo._model

    await kafka_broker.publish(
        dict(
            name=product.name,
            unit=product.unit.name,
            standard_code=product.standard.code,
            categories=set(),
        ),
        topic='products_in',
        headers={'content-type': 'application/json', },
    )

    assert await product_repo.exists(
        where=(model.name == product.name) &
              (model.unit == product.unit) &
              (model.standard_code == product.standard.code),
    )
