import logfire
import ulid
from faststream import Path
from faststream.nats import NatsResponse, NatsRouter

import constants
from center.testing.factories import OrganizationCurrentInfoOutFactory

__all__ = (
    'router',
)

router = NatsRouter(prefix='current_info.', )
tags = ['out', 'NATS', 'req-rep', 'organization', ]


@router.subscriber('{organization_ulid}')
async def factory_responder(
        organization_ulid: ulid.ULID = Path()
) -> NatsResponse:
    logfire.info(
        f'Got a current info request for organization {organization_ulid}',
        organization_ulid=organization_ulid,
        _tags=tags
    )
    data = OrganizationCurrentInfoOutFactory.build(id=organization_ulid)
    logfire.info('Current plan data', data=data, _tags=tags)
    return NatsResponse(
        body=data,
        headers={'token': constants.ORGANIZATION_TEST_TOKEN},
    )

