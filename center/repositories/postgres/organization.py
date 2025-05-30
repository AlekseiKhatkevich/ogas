from typing import TYPE_CHECKING, Optional

import sqlalchemy as sa

from center.orm_models import OrganizationORM
from common.repositories.postgres import CommonPostgresRepository

if TYPE_CHECKING:
    from ulid import ULID

__all__ = (
    'OrganizationPostgresRepository',
)


class OrganizationPostgresRepository(CommonPostgresRepository, model=OrganizationORM):

    async def get_organization_by_header(
            self,
            _id: Optional['ULID'],
            name: str | None,
            header: str,
    ) -> OrganizationORM | None:
        async with self._db.async_session as session:
            # noinspection PyTypeChecker
            organization = await session.scalar(
                sa.select(
                    self._model,
                ).where(
                    self._model.id == _id if _id is not None else self._model.name == name,
                    self._model.token == sa.func.crypt(header, self._model.token),
                )
            )
            return organization
