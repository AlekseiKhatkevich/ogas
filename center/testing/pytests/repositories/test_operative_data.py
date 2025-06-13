import ulid

from center.orm_models import OperativeDataORM


async def test_insert_data_positive(operative_data_in_factory, operative_data_repo):
    organization_id = ulid.ULID()
    op_data = operative_data_in_factory.batch(size=2, organization_id=organization_id)

    await operative_data_repo.insert_data(op_data)

    assert await operative_data_repo.count(
        where=(OperativeDataORM.product_id.in_(od.product_id for od in op_data)) &
              (OperativeDataORM.organization_id == organization_id) &
              (OperativeDataORM.diff.in_(od.diff for od in op_data)) &
              (OperativeDataORM.change_datetime.in_(od.change_datetime for od in op_data))
    ) == len(op_data)
