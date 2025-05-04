from functools import cached_property

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from common import settings


class Database:
    def __init__(self, pg_dsn: str) -> None:
        self.pg_dsn = pg_dsn

    @cached_property
    def engine(self) -> AsyncEngine:
        return create_async_engine(self.pg_dsn)


db = Database(settings.POSTGRES_DSN.unicode_string())
