import datetime
from typing import Any

from alembic.operations import Operations
from sqlalchemy import DDLElement
from sqlalchemy.ext import compiler


class BaseTimescaleORMMixin:
    timescale_options = None
    retention_policy: datetime.timedelta
    retention_interval: datetime.timedelta
    columnstore_policy_interval: datetime.timedelta
    partition_by: str
    partition_interval: datetime.timedelta

    @classmethod
    def add_columnstore_policy(cls, op: Operations) -> None:
        op.execute(AddColumnstorePolicy(cls.__table__.fullname, cls.columnstore_policy_interval))

    @classmethod
    def remove_columnstore_policy(cls, op: Operations) -> None:
        op.execute(RemoveColumnstorePolicy(cls.__table__.fullname, ))

    @classmethod
    def add_retention_policy(cls, op: Operations) -> None:
        policy_sql = AddRetentionPolicy(cls.__table__.fullname, cls.retention_policy, cls.retention_interval)
        op.execute(policy_sql)

    @classmethod
    def convert_table_to_hypertable(cls, op: Operations) -> None:
        sql1 = ConvertTableToHypertable(
            cls.__table__.fullname,
            cls.partition_by,
            cls.partition_interval,
        )
        op.execute(sql1)

        sql2 = AlterHyperTable(cls.__table__.fullname, cls.timescale_options)
        op.execute(sql2)


class RemoveColumnstorePolicy(DDLElement):
    def __init__(self, name: str) -> None:
        self.name = name


@compiler.compiles(RemoveColumnstorePolicy)
def compile_remove_columnstore_policy(
        element: RemoveColumnstorePolicy,
        compiler: compiler,
        **kw,
) -> str:
    return "CALL remove_columnstore_policy('{}');".format(element.name)


class AddColumnstorePolicy(DDLElement):
    def __init__(self, name: str, interval: datetime.timedelta) -> None:
        self.name = name
        self.interval = interval


@compiler.compiles(AddColumnstorePolicy)
def compile_add_columnstore_policy(
        element: AddColumnstorePolicy,
        compiler: compiler,
        **kw,
) -> str:
    return "CALL add_columnstore_policy('{}', after => INTERVAL '{} SECONDS');;".format(
        element.name,
        element.interval.total_seconds(),
    )


class AddRetentionPolicy(DDLElement):
    def __init__(self, name, drop_after: datetime.timedelta, retention_interval: datetime.timedelta) -> None:
        self.name = name
        self.drop_after = drop_after
        self.retention_interval = retention_interval


@compiler.compiles(AddRetentionPolicy)
def compile_add_retention_policy(element: AddRetentionPolicy, compiler: compiler, **kw) -> str:
    return "SELECT add_retention_policy('{}', INTERVAL '{} seconds', schedule_interval := INTERVAL '{}');".format(
        element.name,
        element.drop_after.total_seconds(),
        element.retention_interval.total_seconds(),
    )


class AlterHyperTable(DDLElement):
    def __init__(self, name: str, timescale_options: dict[str, Any]) -> None:
        self.name = name
        self.timescale_options = timescale_options


@compiler.compiles(AlterHyperTable)
def compile_alter_hypertable(
        element: AlterHyperTable,
        compiler: compiler,
        **kw,
) -> str:
    return "ALTER TABLE {} SET({});".format(
        element.name,
        ', '.join(f"{k} = '{v}'" for k, v in element.timescale_options.items()),
    )


class ConvertTableToHypertable(DDLElement):
    def __init__(
            self,
            name: str,
            partition_by: str,
            partition_interval: datetime.timedelta,
    ):
        self.name = name
        self.partition_by = partition_by
        self.partition_interval = partition_interval


@compiler.compiles(ConvertTableToHypertable)
def compile_convert_table_to_hypertable(
        element: ConvertTableToHypertable,
        compiler: compiler,
        **kw,
) -> str:
    return "SELECT create_hypertable('{}', by_range('{}', INTERVAL '{} SECONDS'));".format(
        element.name,
        element.partition_by,
        element.partition_interval.total_seconds(),
    )
