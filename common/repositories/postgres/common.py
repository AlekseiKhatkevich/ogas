import datetime
from abc import ABC
from dataclasses import dataclass
from typing import Any, ClassVar, TYPE_CHECKING

import sqlalchemy as sa
import ulid
from sqlalchemy.dialects import postgresql as pg
from sqlalchemy.sql._typing import ColumnExpressionArgument

from center.enums import Period, Role
from common.enums.product import ProductUnit
from common.resources.database.postgres.database import Database, db

if TYPE_CHECKING:
    from common.resources.database.postgres.alchemy_related import Base

__all__ = (
    'AbstractPostgresRepository',
    'CommonPostgresRepository',
    'UpsertResult',
    'InfoForSchedule',
    'InfoForPlanning',
)


@dataclass
class InfoForPlanning:
    product_id: ulid.ULID
    to_produce: float
    fact_time: datetime.datetime
    producer_id: ulid.ULID | None
    capability: float | None
    capability_interval: Period | None
    is_warehouse: bool
    product_unit: ProductUnit
    common_capacity_per_hour: float | None = None

    @property
    def plan(self) -> float | int:
        raw_plan = self.to_produce * self.share
        if self.product_unit != ProductUnit.IN_BULK:
            plan = round(raw_plan)
        else:
            plan = raw_plan

        return plan

    @property
    def share(self) -> float:
        return self.capability_per_hour / self.common_capacity_per_hour

    @property
    def no_producer(self) -> bool:
        return self.producer_id is None

    @property
    def can_not_produce(self) -> bool:
        return self.no_producer or self.is_warehouse

    @property
    def capability_per_hour(self) -> float:
        return self.capability / self.capability_interval.to_hours


@dataclass
class InfoForSchedule:
    product_id: ulid.ULID
    role: 'Role'
    in_stock: float
    cons_per_hour: float | None
    necessity: float | None
    capability_per_interval: float
    min_level: float
    capability_interval: 'Period'
    avg_interval: datetime.timedelta


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
    def insert(self) -> pg.Insert:
        return pg.insert(self._model)

    @property
    def select(self) -> sa.Select:
        return sa.select(self._model)

    @property
    def update(self) -> sa.Update:
        return sa.update(self._model)

    @property
    def select_active(self) -> sa.Select:
        return self.select.where(self._model.is_active == sa.true()) if self.has_is_active else self.select

    @property
    def has_is_active(self) -> bool:
        return 'is_active' in self._model.__table__.columns

    async def exists(self, _id: Any | None = None, /, *args, **kwargs) -> int:
        if _id is not None:
            kwargs['where'] = (self._model.id == _id)
        return await self.count(*args, **kwargs)

    async def count(
            self,
            is_active: bool = True,
            where: ColumnExpressionArgument | None = None,
    ) -> int:
        query = sa.select(sa.func.count(sa.literal('*')))
        if is_active and self.has_is_active:
            query = query.where(self._model.is_active == sa.true())
        if where is not None:
            query = query.where(where)
        async with self._db.async_session as session:
            return await session.scalar(query)

    async def refresh(self, instance: M, **kwargs) -> M:
        async with self._db.async_session as session:
            session.add(instance)
            await session.refresh(instance, **kwargs)
            return instance

    async def add_all(self, instances: list[M]) -> list[M]:
        async with self._db.async_session as session:
            session.add_all(instances)
            await session.commit()
            return instances

    async def fetch_one(self, _id: Any = None) -> M | None:
        stmt = sa.select(self._model)
        if _id is not None:
            stmt = stmt.where(self._model.id == _id)
        async with self._db.async_session as session:
            res = await session.scalars(stmt)
            return res.first()
