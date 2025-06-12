import contextvars
from typing import Annotated
from faststream import Depends, apply_types
import ulid
from faststream import Context, Depends, Header, context
from faststream.kafka.message import KafkaMessage

from center.orm_models import OrganizationORM
from center.repositories.postgres import OrganizationPostgresRepository
from common.exceptions.app import AuthMessageException, NoOrganizationIdentityException

__all__ = (
    'organization',
    'CurrentOrganizationDep',
    'CurrentOrganizationDepBatch',
    'current_organization_name',
)

current_organization_name = contextvars.ContextVar('current_organization_name')


def organization_repo() -> OrganizationPostgresRepository:
    return OrganizationPostgresRepository()


@apply_types
async def get_organization_instance(
        organization_id,
        organization_name,
        token,
        repo: OrganizationPostgresRepository = Depends(organization_repo)
    ):
    if organization_id is None and organization_name is None:
        raise NoOrganizationIdentityException(
            'Не указаны organization_id или organization_name. Укажите одно из двух.',
        )
    organization_instance = await repo.get_organization_by_token(organization_id, organization_name, token)
    if organization_instance is None:
        raise AuthMessageException(
            f'Компания с названием "{organization_name}" и id "{organization_id}" не существует или токен не валиден.'
        )
    return organization_instance


async def organization(
        token: str = Header(),
        organization_id: ulid.ULID | None = Header(default=None, cast=True),
        organization_name: str | None = Header(default=None),
) -> OrganizationORM:
    organization_instance = await get_organization_instance(organization_id, organization_name, token)
    context.set_local('current_organization', organization_instance)
    current_organization_name.set(organization_instance.name)
    return organization_instance


async def organization_batch(
        message: KafkaMessage = Context()
) -> list[OrganizationORM | None]:
    organization_instances = []
    for header in message.batch_headers:
        token = header.get('token')
        organization_id = header.get('organization_id')
        organization_name = header.get('organization_id')
        organization_instance = await get_organization_instance(organization_id, organization_name, token)
        organization_instances.append(organization_instance)

    return organization_instances



CurrentOrganizationDep = Annotated[OrganizationORM | None, Depends(organization)]
CurrentOrganizationDepBatch = Annotated[list[OrganizationORM | None], Depends(organization_batch)]
