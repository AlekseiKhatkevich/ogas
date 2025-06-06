from center.faststream.organization import organization_out_publisher, update_organization


async def test_update_organization_name_updated(
        organization_in_db,
        organization_repo,
        organization_token,
        organization_update_in_factory,
        kafka_broker,
):
    data_in = organization_update_in_factory.build()
    kafka_message = dict(
            new_name=data_in.new_name,
            new_token=data_in.new_token.get_secret_value(),
        )

    await kafka_broker.publish(
        message=kafka_message,
        topic='organizations_update',
        headers={
            'content-type': 'application/json',
            'organization_name': organization_in_db.name,
            'token': organization_token,
        },
    )

    assert await organization_repo.get_organization_by_token(
        _id=None,
        name=data_in.new_name ,
        token=data_in.new_token.get_secret_value(),
    )
    update_organization.mock.assert_called_once_with(kafka_message)
    organization_out_publisher.mock.assert_called_once()
