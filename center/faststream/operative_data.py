from faststream.kafka import KafkaRouter
from prometheus_client import Summary
from center.faststream.dependencies import CurrentOrganizationDepBatch
from common.faststream.filters import contentype_json
from ..serializers import OperativeDataIn
from ..usecases.operative_data import OperativeDataInSaveUseCase

__all__ = (
    'receive_operative_data',
)

router = KafkaRouter(prefix='operative_data_', )

handler_summary = Summary(
    'receive_operative_data_latency_seconds',
    'Кумулятивное время работы обработчика receive_operative_data.',
)


@router.subscriber(
    'in',
    filter=contentype_json,
    title='Operative_data-from-organizations.',
    batch=True,
    max_records=1000,
    batch_timeout_ms=1000 * 5,  # msec.
    auto_commit_interval_ms=1000 * 1,
    group_id='operative_data_in_group',
)
@handler_summary.time()
async def receive_operative_data(op_info: list[OperativeDataIn],
                                 organizations: CurrentOrganizationDepBatch,
                                 ) -> None:
    use_case = await OperativeDataInSaveUseCase(op_info, organizations)
    await use_case.execute()
