from typing import TYPE_CHECKING

from faststream import Context, Depends
from faststream.kafka import KafkaRouter

from center.serializers import CapabilityIn
from center.usecases.capability import UpdateCapabilitiesUseCase
from common.faststream.filters import contentype_json
from .dependencies import organization

if TYPE_CHECKING:
    from ..orm_models import OrganizationORM

__all__ = (
    'router',
    'capability_out_publisher',
    'create_or_update_capability',
)


router = KafkaRouter(prefix='capabilities_', dependencies=[Depends(organization)])

capability_out_publisher = router.publisher('out', title='Response-for-capabilities_in')


@router.subscriber('in', filter=contentype_json, title='Receive-capability-info-from-organization.')
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
    return_message = {'created': res.cnt_created, 'updated': res.cnt_updated}
    await capability_out_publisher.publish(
        message=return_message,
        no_confirm=True,
        topic=f'capabilities_out_{current_organization.name}',
    )
    return return_message
