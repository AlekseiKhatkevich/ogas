from faststream import Depends
from faststream.kafka import KafkaRouter

from center.serializers import CapabilityIn
from center.usecases.capability import UpdateCapabilitiesUseCase
from common.faststream.filters import contentype_json
from .dependencies import organization
from ..orm_models import OrganizationORM

__all__ = (
    'router',
    'capability_out_publisher',
    'create_or_update_capability',
)

router = KafkaRouter(prefix='capabilities_', dependencies=[Depends(organization)])

capability_out_publisher = router.publisher('out')


@router.subscriber('in', filter=contentype_json)
@capability_out_publisher
async def create_or_update_capability(
        capabilities: set[CapabilityIn],
        _organization: OrganizationORM | None = Depends(organization),
) -> dict:
    """
    Принимает данные о производительностях от компании и записывает их в БД.
    """
    for c in capabilities:
        # noinspection PyTypeChecker
        c.organization_name = _organization.name
    use_case = UpdateCapabilitiesUseCase(capabilities)
    res = await use_case.execute()
    return {'created': res.cnt_created, 'updated': res.cnt_updated}
