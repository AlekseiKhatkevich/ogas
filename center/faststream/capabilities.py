from typing import TYPE_CHECKING

from faststream import Context, Depends
from faststream.kafka import KafkaRouter

from center.serializers import CapabilityIn
from center.usecases.capability import UpdateCapabilitiesUseCase
from common.faststream.filters import contentype_json
from .dependencies import organization
from .dependencies.middleware import current_organization_topic_middleware

if TYPE_CHECKING:
    from ..orm_models import OrganizationORM

__all__ = (
    'router',
    'capability_out_publisher',
    'create_or_update_capability',
)


router = KafkaRouter(prefix='capabilities_', dependencies=[Depends(organization)])


# noinspection PyTypeChecker
capability_out_publisher = router.publisher(
    'out',
    title='Response-for-capabilities_in',
    middlewares=[current_organization_topic_middleware],
)


@router.subscriber('in', filter=contentype_json, title='Receive-capability-info-from-organization.')
@capability_out_publisher
async def create_or_update_capability(
        capabilities: set[CapabilityIn],
        current_organization: 'OrganizationORM' = Context(),
) -> dict:
    """
    Принимает данные о производительностях от компании и записывает их в БД.
    """
    for c in capabilities:
        # noinspection PyTypeChecker
        c.organization_name = current_organization.name
    use_case = UpdateCapabilitiesUseCase(capabilities)
    res = await use_case.execute()
    return {'created': res.cnt_created, 'updated': res.cnt_updated}
