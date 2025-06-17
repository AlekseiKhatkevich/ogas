import sqlalchemy as sa
from alembic.operations import Operations
from sqlalchemy.ext import compiler
from sqlalchemy_utils.view import CreateView, DropView

DEFAULT_TIMESCALE_OPTIONS = {'timescaledb.continuous': True}


class BaseMatViewORMMixin:
    selectable: sa.Select = None
    __table__: sa.Table = None
    timescale_options = None
    is_view = True

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
