from functools import cached_property

import pydantic_core
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from common import settings


class Database:
    def __init__(self, **kwargs) -> None:
        self._kwargs = kwargs

    @cached_property
    def engine(self) -> AsyncEngine:
        return create_async_engine(
            url=settings.POSTGRES_DSN.unicode_string(),
            execution_options={},
            insertmanyvalues_page_size=2000,
            json_deserializer=pydantic_core.from_json,
            json_serializer=pydantic_core.to_json,
            echo=settings.POSTGRES_ECHO,
            max_overflow=settings.POSTGRES_POOL_OVERFLOW,
            pool_pre_ping=settings.POSTGRES_POOL_PRE_PING,
            **self._kwargs,
        )


db = Database()
