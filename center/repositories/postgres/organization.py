import functools
import operator
from typing import Optional, TYPE_CHECKING
from prometheus_client import Counter
import cachetools
import sqlalchemy as sa

from center.orm_models import OrganizationORM
from common import settings
from common.repositories.postgres import CommonPostgresRepository

if TYPE_CHECKING:
    from ulid import ULID
    from center.serializers import AuthStatus, OrganizationUpdateIn

__all__ = (
    'OrganizationPostgresRepository',
)


class OrganizationPostgresRepository(CommonPostgresRepository, model=OrganizationORM):
    ttl = 60 * 10
    maxsize = 1024
    cache = cachetools.TTLCache(maxsize=maxsize, ttl=ttl)

    auth_attempt_c = Counter(
        'auth_attempt',
        'Попытка аутентификации организации.',
    )
    auth_attempt_cache_miss_c = Counter(
        'auth_attempt_cache_miss',
        'Аутентификация организации из БД.',
    )

    async def get_organization_by_token(
            self,
            _id: Optional['ULID'],
            name: str | None,
            token: str,
    ) -> OrganizationORM | None:
        self.auth_attempt_c.inc()
        organization = self.cache.get(_id) or self.cache.get(name)
        if organization is None:
            self.auth_attempt_cache_miss_c.inc()
            async with self._db.async_session as session:
                # noinspection PyTypeChecker
                organization = await session.scalar(
                    self.select_active.where(
                        self._model.id == _id if _id is not None else self._model.name == name,
                        self._model.token == sa.func.crypt(token, self._model.token),
                    )
                )
                if organization is not None:
                    self.cache.update({organization.name: organization, organization.id: organization})
        return organization

    async def get_organizations_by_token(self, auth_data: list['AuthStatus']) -> list['AuthStatus']:
        #  Заполнили организации из кеша.
        auth_query_conditions = []
        for data in auth_data:
            if data.auth_pair is not None:
                self.auth_attempt_c.inc()
                data.organization = self.cache.get(data.identifier)
                if data.organization is None:
                    self.auth_attempt_cache_miss_c.inc()
                    token = data.auth_pair['token'].get_secret_value()
                    name = data.auth_pair.get('organization_name')
                    _id = data.auth_pair.get('organization_id')
                    auth_query_conditions.append(
                        (self._model.id == _id if _id is not None else self._model.name == name) &
                        (self._model.token == sa.func.crypt(token, self._model.token))
                    )
        #  Получим те, которых нет в кеше из БД.
        if auth_query_conditions:
            query = self.select_active.where(functools.reduce(operator.or_, auth_query_conditions))
            async with self._db.async_session as session:
                res = await session.scalars(query)
                organizations = res.all()

            #  Обновим кеш этими организациями из БД.
            for organization in organizations:
                self.cache.update({organization.name: organization, organization.id: organization})

            #  Проставим организации которых изначально не было в кеше и их получили из БД.
            for data in auth_data:
                if data.organization is None and data.auth_pair:
                    data.organization = self.cache.get(data.header.organization_id) or \
                                        self.cache.get(data.header.organization_name)

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
