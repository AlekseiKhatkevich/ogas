import ulid
from faststream import Depends, Logger, Path
from faststream.nats import JStream, NatsResponse, NatsRouter, ObjWatch
from faststream.nats.annotations import ObjectStorage
from faststream import Response
from center.faststream.dependencies import CurrentOrganizationDep, organization

__all__ = (
    'router',
)

# router = NatsRouter(prefix='current_info_', dependencies=[Depends(organization)])
router = NatsRouter(prefix='current_info.')


@router.subscriber('{organization_ulid}')
async def factory_responder(
        organization_ulid: ulid.ULID = Path()
):
    print('Organization ulid',  ' ', organization_ulid)
    return NatsResponse(
        body='Response from factory.',
        headers={"x-token": "some-token"},
    )

