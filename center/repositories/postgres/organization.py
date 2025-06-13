import functools
import operator
from typing import Optional, TYPE_CHECKING
from common import settings
import sqlalchemy as sa
from cache import AsyncTTL
import cachetools

from center.orm_models import OrganizationORM

from common.repositories.postgres import CommonPostgresRepository

if TYPE_CHECKING:
    from ulid import ULID
    from center.serializers import AuthStatus, OrganizationUpdateIn

__all__ = (
    'OrganizationPostgresRepository',
)


class OrganizationPostgresRepository(CommonPostgresRepository, model=OrganizationORM):
    cache = cachetools.TTLCache(maxsize=99999, ttl=60 * 10)

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

    async def get_organizations_by_token(self, auth_data: list['AuthStatus']) -> list['AuthStatus']:
        #  Заполнили организации из кеша
        auth_query_conditions = []
        for data in auth_data:
            if data.auth_pair:
                data.organization = self.cache.get(data.identifier)
                if data.organization is None:
                    token = data.auth_pair['token'].get_secret_value()
                    name = data.auth_pair.get('organization_name')
                    _id = data.auth_pair.get('organization_id')
                    auth_query_conditions.append(
                        self._model.id == _id if _id is not None else self._model.name == name &
                        self._model.token == sa.func.crypt(token, self._model.token),
                    )
        if auth_query_conditions:
            query = self.select_active.where(
                functools.reduce(operator.or_, auth_query_conditions)
            )
            async with self._db.async_session as session:
                res = await session.scalars(query)
                organizations = res.all()

            org_id_dict = {o.id: o for o in organizations}
            org_name_dict = {o.name: o for o in organizations}

            for _id, organization in org_id_dict.items():
                self.cache[_id] = organization
            for name, organization in org_name_dict.items():
                self.cache[name] = organization

            for data in auth_data:
                if data.organization is None:
                    data.organization = org_id_dict.get(data.header.organization_id) or \
                                        org_name_dict.get(data.header.organization_name)

        return auth_data


    async def update_organization(self, name: str, data: 'OrganizationUpdateIn') -> OrganizationORM | None:
        values = {}
        if data.new_name:
            values['name'] = data.new_name
        if data.new_token:
            raw_token = data.new_token.get_secret_value()
            values['token'] = sa.func.crypt(
                sa.literal(raw_token),
                sa.func.gen_salt(settings.POSTGRES_CRYPTO_HASHER),
            )

        if values:
            stmt = self.update.where(
                self._model.name == name,
            ).values(
                **values
            ).returning(
                self._model,
            )
            async with self._db.async_session as session:
                if data.new_token:
                    await session.execute(sa.text("SET LOCAL log_statement = 'none'"))
                updated_instance = await session.scalar(stmt)
                await session.commit()
                return updated_instance

        return None
