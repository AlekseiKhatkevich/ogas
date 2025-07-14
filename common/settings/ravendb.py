from typing import Annotated

from pydantic import Field, HttpUrl
from pydantic_settings import BaseSettings


class RavenDBSettings(BaseSettings):
    RAVEN_DB_SERVER_URL: Annotated[
        HttpUrl,
        Field(description='Урл RavenDB.', ),
    ]
    RAVEN_DB_DATABASE_NAME: Annotated[
        str,
        Field(description='Название БД в самой RavenDB.')
    ]
