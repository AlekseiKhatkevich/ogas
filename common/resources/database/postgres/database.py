from contextlib import aclosing, asynccontextmanager
from functools import cached_property
from typing import AsyncGenerator

import pydantic_core
import ulid
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from common import settings


class Database:
    def __init__(self,con=None, **kwargs) -> None:
        self._kwargs = kwargs
        self.con=con

    def __new__(cls, **kwargs) -> 'Database':
        if not hasattr(cls, 'instance'):
            cls.instance = super().__new__(cls)
        # noinspection PyUnresolvedReferences
        return cls.instance

    @property
    def engine(self) -> AsyncEngine:
        return create_async_engine(
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

    @property
    def async_sessionmaker(self) -> async_sessionmaker:
        return async_sessionmaker(self.con or self.engine, expire_on_commit=False, join_transaction_mode="create_savepoint")

    @property
    @asynccontextmanager
    async def async_session(self) -> AsyncGenerator[AsyncSession]:
        async with aclosing(self.async_sessionmaker()) as async_session:
            yield async_session

    async def check_health(self) -> bool:
        try:
            async with self.async_session as session:
                await session.execute(text('SELECT 1'))
            return True
        except SQLAlchemyError as e:
            print(f'Database health check failed: {e}')
            return False


db = Database()
