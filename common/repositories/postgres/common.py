from abc import ABC
from dataclasses import dataclass
from typing import Any, ClassVar, Sequence, TYPE_CHECKING

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

    @property
    def ids(self) -> list[T]:
        return self.ids_created + self.ids_updated


class AbstractPostgresRepository(ABC):
    _model: ClassVar['Base']

    def __init__(self, _db: Database = db, /, ) -> None:
        self._db = db


class CommonPostgresRepository[M:'Base'](AbstractPostgresRepository):
    def __init_subclass__(cls, model: M, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._model: M = model

    @property
    def select(self) -> sa.Select:
        return sa.select(self._model)

    async def exists(self, _id: Any | None = None, /, *args, **kwargs) -> int:
        if _id is not None:
            kwargs['where'] = (self._model.id == _id)
        return await self.count(*args, **kwargs)

    async def count(
            self,
            is_active: bool = True,
            where: ColumnExpressionArgument | None = None,
    ) -> int:
        query = sa.select(sa.func.count(self._model.id))
        if is_active and ('is_active' in self._model.__table__.columns):
            query = query.where(self._model.is_active == sa.true())
        if where is not None:
            query = query.where(where)
        async with self._db.async_session as session:
            return await session.scalar(query)
