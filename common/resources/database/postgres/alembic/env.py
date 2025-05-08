import asyncio
from logging.config import fileConfig

import alembic_postgresql_enum  # do not remove !
from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from common import settings
from common.orm_models import *  # Do not remove !!!
from common.orm_models.custom_types import ULID
from common.resources.database.postgres import Base
from common.resources.database.postgres.alembic.utils.rewriters import writer
from common.utils import get_all_subclasses

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


extra_common_kwargs = dict(
        compare_server_default=True,
        process_revision_directives=writer,
        user_module_prefix="common.orm_models.custom_types.",
    )


def check_all_column_comments() -> None:
    """
    Проверяем чтобы все поля имели комменты.
    """
    for subclass in get_all_subclasses(Base):
        # noinspection PyTypeChecker
        for column in subclass.__table__.columns:
            if column.comment is None:
                raise AttributeError(
                    f'Comment on column "{column.name}" in model "{subclass.__name__}" is not defined.'
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
    #  Регистрация кастомных типов, чтобы не получать
    #  SAWarning: Did not recognize type 'ulid' of column 'id'
    #  https://github.com/sqlalchemy/alembic/discussions/1324
    connection.dialect.ischema_names['ulid'] = ULID
    check_all_column_comments()

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
