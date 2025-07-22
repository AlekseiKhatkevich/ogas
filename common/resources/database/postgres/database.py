from contextlib import aclosing, asynccontextmanager
from functools import lru_cache
from typing import AsyncGenerator

import logfire
import pydantic_core
import ulid
from logfire.integrations.sqlalchemy import CommenterOptions
from prometheus_client import Counter, Histogram
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from common import settings
from common.resources.interfaces import HealthCheckable
from utils.logfire_related import logfire_configure

logfire_configure()


class Database(HealthCheckable):
    _sessionmaker_kwargs = dict(
        expire_on_commit=False,
        join_transaction_mode='create_savepoint',
    )
    health_check_exc_cnt = Counter(
        'postgres_healthcheck_exceptions',
        'Счетчик ошибок связи с Postgres во время старта приложения.'
    )
    session_histogram = Histogram(
        'db_request_latency_seconds',
        'Description of histogram',
        buckets=(
            0.005, 0.007, 0.01, 0.015, 0.020, 0.025,
            0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, float('inf'),
        )
    )

    def __init__(self, connection: AsyncConnection | None = None, **kwargs) -> None:
        self._kwargs = kwargs
        self.connection = connection
        self._maker: async_sessionmaker | None = None

    def __new__(cls, **kwargs) -> 'Database':
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        # noinspection PyUnresolvedReferences
        return cls.instance

    @lru_cache(maxsize=32)
    def _instrument_logfire(self, engine):
        logfire.instrument_sqlalchemy(
            engine=engine,
            enable_commenter=True,
            commenter_options=CommenterOptions(opentelemetry_values=True),
            enable_attribute_commenter=True,
        )

    @property
    def engine(self) -> AsyncEngine:
        engine = create_async_engine(
            **dict(
                url=settings.POSTGRES_DSN.unicode_string(),
                execution_options={},
                insertmanyvalues_page_size=2000,
                json_deserializer=pydantic_core.from_json,
                json_serializer=pydantic_core.to_json,
                echo=settings.POSTGRES_ECHO,
                max_overflow=settings.POSTGRES_POOL_OVERFLOW,
                pool_pre_ping=settings.POSTGRES_POOL_PRE_PING,
                pool_timeout=5,
                pool_size=settings.POSTGRES_POOL_SIZE,
                connect_args={
                    'prepared_statement_name_func': lambda: f'__asyncpg_{ulid.ULID()}__',
                },
            ) | self._kwargs,
        )
        self._instrument_logfire(engine)
        return engine

    @property
    def async_sessionmaker(self) -> async_sessionmaker:
        if self._maker is None:
            self._maker = async_sessionmaker(self.engine, **self._sessionmaker_kwargs)
        if self.connection is not None:
            self._maker.configure(bind=self.connection)
        return self._maker

    @property
    @asynccontextmanager
    async def async_session(self) -> AsyncGenerator[AsyncSession]:
        async with aclosing(self.async_sessionmaker()) as async_session:
            with self.session_histogram.time():
                yield async_session

    async def check_health(self) -> bool:
        try:
            with self.health_check_exc_cnt.count_exceptions((SQLAlchemyError, OSError)):
                async with self.async_session as session:
                    await session.execute(text('SELECT 1'))
                return True
        except (SQLAlchemyError, OSError) as e:
            print(f'Database health check failed: {e}')
            return False

    @property
    def service_name(self) -> str:
        return 'PostgresDB'


db = Database()
