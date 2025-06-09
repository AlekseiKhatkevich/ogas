from typing import TYPE_CHECKING

from faststream import Context, Depends
from faststream.kafka import KafkaRouter

from center.faststream.dependencies import organization
from common.faststream.filters import contentype_json
from ..serializers import OperativeDataIn

if TYPE_CHECKING:
    from ..orm_models import OrganizationORM

__all__ = (
    'receive_operative_data',
)

router = KafkaRouter(prefix='operative_data_', dependencies=[Depends(organization)])


@router.subscriber(
    'in',
    filter=contentype_json,
    title='Consumation-from-organizations.',
    batch=True,
    max_records=1000,
    batch_timeout_ms=1000 * 5,  # msec.
)
async def receive_operative_data(
        messages: list[OperativeDataIn],
        current_organization: 'OrganizationORM' = Context(),
):
    print(messages)
    print(current_organization)
