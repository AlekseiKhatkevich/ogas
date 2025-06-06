from typing import Optional, TYPE_CHECKING

import sqlalchemy as sa
from cache import AsyncTTL

from center.orm_models import OrganizationORM

from common.repositories.postgres import CommonPostgresRepository

if TYPE_CHECKING:
    from ulid import ULID
    from center.serializers import OrganizationUpdateIn

__all__ = (
    'OrganizationPostgresRepository',
)


class OrganizationPostgresRepository(CommonPostgresRepository, model=OrganizationORM):

    @AsyncTTL(time_to_live=60 * 10, maxsize=1024, skip_args=1)
    async def get_organization_by_token(
            self,
            _id: Optional['ULID'],
            name: str | None,
            token: str,
    ) -> OrganizationORM | None:
        async with self._db.async_session as session:
            # noinspection PyTypeChecker
            organization = await session.scalar(
                self.select_active.where(
                    self._model.id == _id if _id is not None else self._model.name == name,
                    self._model.token == sa.func.crypt(token, self._model.token),
                )
            )
            return organization

    async def update_organization(self, name: str, data: 'OrganizationUpdateIn'):
        values = {}
        if data.new_name:
            values['name'] = data.new_name
        if data.new_token:
            values['token'] = data.new_token
