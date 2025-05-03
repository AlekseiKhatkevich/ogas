from pydantic import Field, PostgresDsn
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    PG_DSN: PostgresDsn = Field(repr=False)

