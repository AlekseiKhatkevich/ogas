from faststream.kafka import KafkaRouter

from center.faststream.dependencies import CurrentOrganizationDepBatch
from common.faststream.filters import contentype_json
from ..serializers import OperativeDataIn
from ..usecases.operative_data import OperativeDataInSaveUseCase

__all__ = (
    'receive_operative_data',
)

router = KafkaRouter(prefix='operative_data_', )
from prometheus_client import start_http_server, Summary
import random
import time

# Create a metric to track time spent and requests made.
REQUEST_TIME = Summary('request_huest', 'Time spent processing request')

# Decorate function with metric.
@REQUEST_TIME.time()
def process_request(t):
    """A dummy function that takes some time."""
    time.sleep(t)

@router.subscriber(
    'in',
    filter=contentype_json,
    title='Operative_data-from-organizations.',
    batch=True,
    max_records=1000,
    batch_timeout_ms=1000 * 5,  # msec.
    auto_commit_interval_ms=1000 * 1,
    group_id='operative_data_in_group',
    # max_workers=4
)
async def receive_operative_data(op_info: list[OperativeDataIn],
                                 organizations: CurrentOrganizationDepBatch,
                                 ) -> None:
    use_case = await OperativeDataInSaveUseCase(op_info, organizations)
    process_request(random.random())
    await use_case.execute()
