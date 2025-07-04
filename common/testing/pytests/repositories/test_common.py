from common.enums.product import ProductUnit


def test_info_for_planning(
        info_for_planning_dc_factory,
):
    info = info_for_planning_dc_factory.build()

    assert info.capability_per_hour == info.capability / info.capability_interval.to_hours
    assert not info.can_not_produce

    info_no_producer = info_for_planning_dc_factory.build(producer_id=None)
    info_is_warehouse = info_for_planning_dc_factory.build(is_warehouse=True)

    assert info_no_producer.can_not_produce
    assert info_is_warehouse.can_not_produce

    info.common_capacity_per_hour = 9999999
    assert info.share == info.capability_per_hour / info.common_capacity_per_hour

    info.product_unit = ProductUnit.IN_BULK
    assert info.plan == info.to_produce * info.share

    info.product_unit = ProductUnit.BOX
    assert info.plan == round(info.to_produce * info.share)
