import alembic_postgresql_enum  # do not remove !
from alembic.operations import ops
from alembic.autogenerate import rewriter
import asyncio
from logging.config import fileConfig

from sqlalchemy import Column, pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

from common import settings
from common.resources.database.postgres import Base

from sqlalchemy.sql.sqltypes import Boolean, Enum, Integer, String

from common.orm_models import *   # Do not remove !!!

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


writer = rewriter.Rewriter()


@writer.rewrites(ops.CreateTableOp)
def order_columns(context, revision, op):

    """
    https://www.cybertec-postgresql.com/en/type-alignment-padding-bytes-no-space-waste-in-postgresql/
    """
    # special_names = {"id": -100, "created_at": 1001, "updated_at": 1002}
    #  номер -кол-во байт (alignment)
    # column_type_weights = {
    #     String: 1,
    #     Boolean: 4,
    #     Enum: 1,
    #     Integer: 4,
    # }
    columns_with_weights = []
    for col in op.columns:
        if isinstance(col, Column):
            print(f'Col is isinstance Column')
            print(f'Col type is {col.type}')
            if isinstance(col.type, (String, Enum,)):
                weight = 1
            elif isinstance(col.type, (Boolean, Integer,)):
                weight = 4
            else:
                weight = -999
            print(f'weight is {weight}')
            columns_with_weights.append((weight, col.copy()))

    print(f'Columns with weight {columns_with_weights}')
    columns = [
        col for idx, col in sorted(columns_with_weights, key=lambda entry: entry[0], reverse=True)
    ]
    print(f'Sorted columns {columns}')
    return ops.CreateTableOp(
        op.table_name, columns, schema=op.schema, **op.kw)


extra_common_kwargs = dict(
        compare_server_default=True,
        process_revision_directives=writer,
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = settings.POSTGRES_DSN.unicode_string()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **extra_common_kwargs,
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        **extra_common_kwargs,
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    config.set_main_option('sqlalchemy.url', settings.POSTGRES_DSN.unicode_string())
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

optimization_import_keepers = [alembic_postgresql_enum, ProductORM]
