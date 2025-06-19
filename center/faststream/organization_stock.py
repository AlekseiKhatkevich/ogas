from fast_depends import Depends
from faststream.kafka import KafkaRouter

from center.faststream.dependencies import CurrentOrganizationDep, organization
from center.serializers import OrganizationStockIn
from center.usecases.organization_stock import OrganizationStockSaveUseCase
from common.faststream.filters import contentype_json

router = KafkaRouter(prefix='organization_stock_', dependencies=[Depends(organization)])


@router.subscriber(
    'in',
    filter=contentype_json,
    title='Organization-stock',
    auto_commit_interval_ms=1000 * 1,
    group_id='organization_stock_in_group',
    # max_workers=1
)
async def receive_organization_stock_data(stock: OrganizationStockIn) -> None:
    use_case = await OrganizationStockSaveUseCase(stock)
    await use_case.execute()
