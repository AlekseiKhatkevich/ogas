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

    async def insert_data(self, data: list['OperativeDataIn']) -> list[OperativeDataORM]:
        instances = [
            OperativeDataORM(
                **d.model_dump(warnings='warn')
            ) for d in data
        ]
        return await self.add_all(instances)
