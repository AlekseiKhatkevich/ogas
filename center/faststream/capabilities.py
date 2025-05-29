from faststream.kafka import KafkaRouter

from center.serializers import CapabilityIn
from center.usecases.capability import UpdateCapabilitiesUseCase
from common.faststream.filters import contentype_json

__all__ = (
    'router',
)

router = KafkaRouter(prefix='capabilities_')

capability_out_publisher = router.publisher('out')


@router.subscriber('in', filter=contentype_json)
@capability_out_publisher
async def create_or_update_capability(capabilities: set[CapabilityIn]) -> dict:
    """
    Принимает данные о производительностях от компании и записывает их в БД.
    """
    use_case = UpdateCapabilitiesUseCase(capabilities)
    res = await use_case.execute()
    return {'created': res.cnt_created, 'updated': res.cnt_updated}
