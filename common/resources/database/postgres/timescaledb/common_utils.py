import datetime

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
    def convert_table_to_hypertable(cls, op: Operations) -> None:
        sql1 = ConvertTableToHypertable(
            cls.__table__.fullname,
            cls.partition_by,
            cls.partition_interval,
        )
        op.execute(sql1)

        sql2 = AlterHyperTable(cls.__table__.fullname, cls.timescale_options)
        op.execute(sql2)


class AlterHyperTable(DDLElement):
    def __init__(self, name, timescale_options):
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
            name,
            partition_by,
            partition_interval,
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
