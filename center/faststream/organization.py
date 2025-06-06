from faststream import Depends
from faststream.kafka import KafkaRouter

from center.faststream.dependencies import organization
from center.serializers import OrganizationUpdateIn
from common.faststream.filters import contentype_json

router = KafkaRouter(prefix='organizations_', dependencies=[Depends(organization)])
organization_out_publisher = router.publisher(
    'org_name_changed',
    title='Organization-name-changed',
)


@router.subscriber('update', filter=contentype_json, title='update-organization')
async def update_organization(
        data: OrganizationUpdateIn,
        # current_organization: CurrentOrganizationDep,
):
    pass