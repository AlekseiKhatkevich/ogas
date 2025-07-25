from typing import Annotated

from pydantic import Field, NatsDsn
from pydantic_settings import BaseSettings


class NatsSettings(BaseSettings):
    NATS_DSN: Annotated[
        NatsDsn,
        Field(repr=False, description='Урл NATS сервера.', ),
    ]
