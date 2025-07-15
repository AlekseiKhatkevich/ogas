import pathlib
from typing import Annotated

from pydantic import AfterValidator, Field
from pydantic_settings import BaseSettings


class CommonSettings(BaseSettings):
    BASE_DIR: Annotated[
        pathlib.Path,
        Field(
            frozen=True,
            description='Корень проекта.',
            default_factory=lambda: pathlib.Path.cwd(),
            exclude=True,
        )]
    APP_NAME: Annotated[
        str,
        AfterValidator(lambda v: v.lower()),
        Field(description='Наименование сервиса.'),
    ]
