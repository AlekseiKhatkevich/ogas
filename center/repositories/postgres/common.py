from abc import ABC
from typing import ClassVar, Iterable, Sized, TYPE_CHECKING, Any
import sqlalchemy as sa
from dataclasses import dataclass

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
    ids: tuple[T, ...]
    cnt_created: int
    cnt_updated: int


class AbstractPostgresRepository(ABC):
    _model: ClassVar['Base']

    def __init__(self, _db: Database = db, /, ) -> None:
        self._db = db


class CommonPostgresRepository[M:'Base'](AbstractPostgresRepository):
    def __init_subclass__(cls, model: M, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._model: M = model

    async def exists(self, ids: Sized[Any], is_active: bool = True) -> bool:
        """
        Существуют ли все записи с такими id в бд.
        :param ids: набор id
        :param is_active: нужно ли фильтровать по полю 'is_active'
        :return: bool
        """
        query = sa.select(sa.func.count(self._model.id)).where(self._model.id.in_(ids))
        if is_active and ('is_active' in self._model.__table__.columns):
            query = query.where(self._model.is_active == sa.true())

        async with self._db.async_session as session:
            res = await session.scalar(query)
            return res == len(ids)
