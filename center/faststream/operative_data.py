from faststream import Depends
from faststream.kafka import KafkaRouter

from center.faststream.dependencies import organization
from common.faststream.filters import contentype_json
from ..serializers import OperativeDataIn
from ..usecases.operative_data import OperativeDataInSaveUseCase

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
    batch_timeout_ms=1000 * 20,  # msec.
)
async def receive_operative_data(
        op_info: list[OperativeDataIn],
):
    use_case = await OperativeDataInSaveUseCase(op_info=op_info)
    await use_case.execute()
