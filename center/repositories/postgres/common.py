from abc import ABC
from dataclasses import dataclass
from typing import ClassVar, Sequence, TYPE_CHECKING

import sqlalchemy as sa
from sqlalchemy.sql._typing import ColumnExpressionArgument

from common.resources.database.postgres.database import Database, db

if TYPE_CHECKING:
    from common.resources.database.postgres.alchemy_related import Base

__all__ = (
    'AbstractPostgresRepository',
    'CommonPostgresRepository',
    'UpsertResult',
)


@dataclass
class UpsertResult[T]:
    ids_created: list[T]
    ids_updated: list[T]

    @property
    def cnt_created(self) -> int:
        return len(self.ids_created)

    @property
    def cnt_updated(self) -> int:
        return len(self.ids_updated)


class AbstractPostgresRepository(ABC):
    _model: ClassVar['Base']

    def __init__(self, _db: Database = db, /, ) -> None:
        self._db = db


class CommonPostgresRepository[M:'Base'](AbstractPostgresRepository):
    def __init_subclass__(cls, model: M, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._model: M = model

    async def exists(
            self,
            ids: Sequence,
            is_active: bool = True,
            where: ColumnExpressionArgument | None = None,
    ) -> bool:
        """
        Существуют ли все записи с такими id в бд.
        :param where: Набор дополнительных фильтров для поиска.
        :param ids: Набор id.
        :param is_active: Нужно ли фильтровать по полю 'is_active'.
        :return: Таки есть ли все записи или их нет?
        """
        query = sa.select(sa.func.count(self._model.id)).where(self._model.id.in_(ids))
        if where is not None:
            query = query.where(where)
        if is_active and ('is_active' in self._model.__table__.columns):
            query = query.where(self._model.is_active == sa.true())

        async with self._db.async_session as session:
            res = await session.scalar(query)
            return res == len(ids)
