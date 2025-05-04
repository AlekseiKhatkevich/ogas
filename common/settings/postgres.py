from typing import Annotated

from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    POSTGRES_DSN: Annotated[
        PostgresDsn,
        Field(repr=False, description='Урл БД Postgres,'),
    ]
