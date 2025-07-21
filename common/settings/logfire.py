import os
from typing import Annotated

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings


class LogfireSettings(BaseSettings):
    LOGFIRE_TOKEN: Annotated[
        str,
        Field(repr=False, description='Logfire write token',),
    ]
