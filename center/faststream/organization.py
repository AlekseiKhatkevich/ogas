from faststream import Depends
from faststream.kafka import KafkaRouter

from center.faststream.dependencies import CurrentOrganizationDep, organization
from center.serializers import OrganizationUpdateIn
from center.usecases.organization import OrganizationUpdateUseCase
from common.faststream.filters import contentype_json

router = KafkaRouter(prefix='organizations_', dependencies=[Depends(organization)])

organization_out_publisher = router.publisher(
    'name_changed',
    title='Organization-name-changed',
)


@router.subscriber('update', filter=contentype_json, title='update-organization')
async def update_organization(
        data: OrganizationUpdateIn,
        current_organization: CurrentOrganizationDep,
):
    use_case = OrganizationUpdateUseCase(current_organization.name, data, organization_out_publisher)
    await use_case.execute()
