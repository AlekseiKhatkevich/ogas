import pytest
from faststream.exceptions import SubscriberNotFound

from faststream_serve import capability_out_publisher, create_or_update_capability


async def test_create_or_update_capability_positive(
        capability_in_factory,
        kafka_broker,
        organization_in_db,
        product_in_db,
        capabilities_repo,
):
    capability = capability_in_factory.build(
        organization_name=organization_in_db.name,
        product_id=product_in_db.id,
    )
    await kafka_broker.publish([capability], topic='capability_in')

    assert await capabilities_repo.count() == 1
    create_or_update_capability.mock.assert_called_once_with([capability.model_dump()])
    capability_out_publisher.mock.assert_called_once_with({'created': 1, 'updated': 0})


async def test_create_or_update_capability_negative(
        capability_in_factory,
        kafka_broker,
):
    capability = capability_in_factory.build()

    with pytest.raises(SubscriberNotFound):
        await kafka_broker.publish(
            [capability],
            topic='capability_in',
            headers={'content-type': 'fucking/bullshit'},
        )
