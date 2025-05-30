from faststream import Header, Depends
from faststream.kafka import KafkaRouter
from common.resources.database.postgres import db
from center.serializers import CapabilityIn
from center.usecases.capability import UpdateCapabilitiesUseCase
from common.faststream.filters import contentype_json

__all__ = (
    'router',
    'capability_out_publisher',
    'create_or_update_capability',
)

router = KafkaRouter(prefix='capabilities_')

capability_out_publisher = router.publisher('out')


# def db():
#     return db

class AppException(Exception):
    pass


class MessageException(AppException):
    pass


class MessageHeaderException(MessageException):
    pass


class NoOrganizationIdentityException(MessageHeaderException):
    pass


def organization(
        token=Header(),
        organization_id=Header(default=None),
        organization_name=Header(default=None),
):
    if organization_id is None and organization_name is None:
        raise NoOrganizationIdentityException(
            'Не указаны organization_id или organization_name. Укажите одно из двух',
        )



@router.subscriber('in', filter=contentype_json)
@capability_out_publisher
async def create_or_update_capability(capabilities: set[CapabilityIn], token: str = Header()) -> dict:
    """
    Принимает данные о производительностях от компании и записывает их в БД.
    """
    print('token', token)
    use_case = UpdateCapabilitiesUseCase(capabilities)
    res = await use_case.execute()
    return {'created': res.cnt_created, 'updated': res.cnt_updated}
