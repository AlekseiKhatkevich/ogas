

async def test_insert_operative_data(
        kafka_broker,
        operative_data_in_factory,
        organization_in_db,
        organization_token,
        operative_data_repo,
):
    data_in = operative_data_in_factory.build()
    await kafka_broker.publish(
        message=data_in.model_dump_json(),
        topic='operative_data_in',
        headers={
            'content-type': 'application/json',
            'organization_name': organization_in_db.name,
            'token': organization_token,
        },
    )
    assert await operative_data_repo.count() == 1
