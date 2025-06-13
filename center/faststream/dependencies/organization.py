import contextvars
from typing import Annotated

import ulid
from faststream import Context, Depends, Header, apply_types, context

from center.orm_models import OrganizationORM
from center.repositories.postgres import OrganizationPostgresRepository
from center.serializers import AuthStatus, kafka_header_list_adapter
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
        organization_id: ulid.ULID,
        organization_name: str,
        token: str,
        repo: OrganizationPostgresRepository = Depends(organization_repo)
    ) -> OrganizationORM:
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
        batch_headers: dict[str, str] = Context('message.batch_headers'),
        repo: OrganizationPostgresRepository = Depends(organization_repo)
) -> list[OrganizationORM | None]:
    auth_statuses = [
        AuthStatus(header=header) for header in kafka_header_list_adapter.validate_python(batch_headers)
    ]
    auth_statuses_filled = await repo.get_organizations_by_token(auth_statuses)

    return [auth_status.organization for auth_status in auth_statuses_filled]



CurrentOrganizationDep = Annotated[OrganizationORM | None, Depends(organization)]
CurrentOrganizationDepBatch = Annotated[list[OrganizationORM | None], Depends(organization_batch)]
