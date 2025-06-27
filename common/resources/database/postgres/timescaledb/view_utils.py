import datetime

import sqlalchemy as sa
from alembic.operations import Operations
from sqlalchemy import DDLElement
from sqlalchemy.ext import compiler
from sqlalchemy_utils.view import CreateView, DropView

from common.resources.database.postgres.timescaledb.common_utils import BaseTimescaleORMMixin

DEFAULT_TIMESCALE_OPTIONS = {'timescaledb.continuous': True}


class BaseMatViewORMMixin(BaseTimescaleORMMixin):
    selectable: sa.Select = None
    __table__: sa.Table = None
    is_view = True
    continuous_aggregate_start_offset: datetime.timedelta
    continuous_aggregate_end_offset: datetime.timedelta
    continuous_aggregate_schedule_interval: datetime.timedelta

    @classmethod
    def create(cls, op: Operations) -> None:
        """Используется только в миграциях alembic"""
        cls.drop(op)
        create_sql = CreateTimescaleView(
            cls.__table__.fullname,
            cls.selectable,
            materialized=True,
            timescale_options=cls.timescale_options,
        )
        op.execute(create_sql)
        for idx in cls.__table__.indexes:
            idx.create(op.get_bind())

    @classmethod
    def drop(cls, op: Operations) -> None:
        """Используется только в миграциях alembic"""
        drop_sql = DropView(cls.__table__.fullname, materialized=True, cascade=True)
        op.execute(drop_sql)

    @classmethod
    def update(cls, op: Operations) -> None:
        """Используется только в миграциях alembic
        Основано на:
        https://stackoverflow.com/questions/64653231/add-a-new-column-to-a-postgres-materialized-view
        """
        create_sql = CreateView(f"{cls.__table__.fullname}temp", cls.selectable, materialized=True)
        op.execute(create_sql)

        cls.drop(op)

        op.rename_table(f"{cls.__table__.fullname}temp", cls.__table__.fullname)

        for idx in cls.__table__.indexes:
            idx.create(op.get_bind())

    @classmethod
    def remove_retention_policy(cls, op: Operations) -> None:
        op.execute(RemoveRetentionPolicy(cls.__table__.fullname))

    @classmethod
    def add_continuous_aggregate_policy(cls, op: Operations) -> None:
        sql = AddContinuousAggregatePolicy(
            cls.__table__.fullname,
            start_offset=cls.continuous_aggregate_start_offset,
            end_offset=cls.continuous_aggregate_end_offset,
            schedule_interval=cls.continuous_aggregate_schedule_interval,
        )
        op.execute(sql)

    @classmethod
    def remove_continuous_aggregate_policy(cls, op: Operations) -> None:
        op.execute(RemoveContinuousAggregatePolicy(cls.__table__.fullname))


class RemoveContinuousAggregatePolicy(DDLElement):
    def __init__(self, name: str) -> None:
        self.name = name


@compiler.compiles(RemoveContinuousAggregatePolicy)
def compile_remove_continuous_aggregate_policy(
        element: RemoveContinuousAggregatePolicy,
        compiler: compiler,
        **kw,
) -> str:
    return "SELECT remove_continuous_aggregate_policy('{}');".format(element.name)


class AddContinuousAggregatePolicy(DDLElement):
    def __init__(
            self,
            name: str,
            start_offset: datetime.timedelta,
            end_offset: datetime.timedelta,
            schedule_interval: datetime.timedelta,
    ) -> None:
        self.name = name
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.schedule_interval = schedule_interval


@compiler.compiles(AddContinuousAggregatePolicy)
def compile_add_continuous_aggregate_policy(element: AddContinuousAggregatePolicy, compiler: compiler, **kw) -> str:
    return """
    SELECT add_continuous_aggregate_policy(
    '{}',
    start_offset => INTERVAL '{} SECONDS',
    end_offset => INTERVAL '{} SECONDS',
    schedule_interval => INTERVAL '{} SECONDS');
    """.format(
        element.name,
        element.start_offset.total_seconds(),
        element.end_offset.total_seconds(),
        element.schedule_interval.total_seconds(),
    )


class RemoveRetentionPolicy(DDLElement):
    def __init__(self, name: str) -> None:
        self.name = name


@compiler.compiles(RemoveRetentionPolicy)
def compile_remove_retention_policy(element: RemoveRetentionPolicy, compiler: compiler, **kw) -> str:
    return "SELECT remove_retention_policy('{}');".format(element.name)


class CreateTimescaleView(CreateView):
    def __init__(
            self,
            name,
            selectable,
            materialized,
            replace=False,
            timescale_options=DEFAULT_TIMESCALE_OPTIONS,
    ) -> None:
        super().__init__(name, selectable, materialized, replace)
        self.timescale_options = timescale_options


@compiler.compiles(CreateTimescaleView)
def compile_create_timescale_materialized_view(element: CreateTimescaleView, compiler: compiler, **kw) -> str:
    return 'CREATE {}{}VIEW {} WITH({}) AS {} WITH NO DATA'.format(
        'OR REPLACE ' if element.replace else '',
        'MATERIALIZED ' if element.materialized else '',
        compiler.dialect.identifier_preparer.quote(element.name),
        ', '.join(f'{k} = {v}' for k, v in element.timescale_options.items()),
        compiler.sql_compiler.process(element.selectable, literal_binds=True),
    )
