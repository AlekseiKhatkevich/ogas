from typing import TYPE_CHECKING

import ulid

from center.orm_models import OperativeDataORM
from center.serializers import OperativeDataIn
from common.repositories.postgres import CommonPostgresRepository

if TYPE_CHECKING:
    from center.serializers import OperativeDataIn

__all__ = (
    'OperativeDataPostgresRepository',
)


class OperativeDataPostgresRepository(CommonPostgresRepository, model=OperativeDataORM):

    async def insert_data(self, data: list['OperativeDataIn'], organization_id: ulid.ULID) -> list[OperativeDataORM]:
        instances = [
            OperativeDataORM(**d.model_dump(context={'organization_id': organization_id})) for d in data
        ]
        async with self._db.async_session as session:
            session.add_all(instances)
            await session.commit()

        return instances
