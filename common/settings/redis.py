from typing import Annotated

from pydantic import Field, RedisDsn
from pydantic_settings import BaseSettings


class RedisSettings(BaseSettings):
    REDIS_DSN: Annotated[
        RedisDsn,
        Field(repr=False, description='Урл Redis', ),
    ]