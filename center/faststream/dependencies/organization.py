from typing import Annotated

import ulid
from faststream import Depends, Header

from center.orm_models import OrganizationORM
from center.repositories.postgres import OrganizationPostgresRepository
from common.exceptions.app import AuthMessageException, NoOrganizationIdentityException

__all__ = (
    'organization',
    'CurrentOrganizationDep',
)


def organization_repo() -> OrganizationPostgresRepository:
    return OrganizationPostgresRepository()


async def organization(
        token: str = Header(),
        organization_id: ulid.ULID | None = Header(default=None),
        organization_name: str | None = Header(default=None),
        repo: OrganizationPostgresRepository = Depends(organization_repo, cast=False)
) -> OrganizationORM | None:
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


CurrentOrganizationDep = Annotated[OrganizationORM | None, Depends(organization)]
