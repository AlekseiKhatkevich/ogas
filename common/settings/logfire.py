import os
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class LogfireSettings(BaseSettings):
    LOGFIRE_TOKEN: Annotated[
        str,
        Field(repr=False, description='Logfire write token',),
    ]

    # noinspection PyNestedDecorators
    @field_validator('LOGFIRE_TOKEN', mode='after')
    @classmethod
    def set_env(cls, value: str) -> str:
        if 'LOGFIRE_TOKEN' not in os.environ:
            os.environ['LOGFIRE_TOKEN'] = value
        return value
