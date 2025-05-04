from typing import Annotated

from pydantic import AfterValidator, BeforeValidator, Field, PositiveInt, PostgresDsn
from pydantic_settings import BaseSettings


class PostgresSettings(BaseSettings):
    POSTGRES_DSN: Annotated[
        PostgresDsn,
        Field(repr=False, description='Урл БД Postgres',),
    ]

    POSTGRES_ECHO: Annotated[
        bool,
        Field(description='Вывод SQL команд в консоль',),
    ] = False

    POSTGRES_ECHO_POOL: Annotated[
        bool,
        Field(description='Вывод информации о пуле коннектов в консоль',),
    ] = False

    POSTGRES_POOL_OVERFLOW: Annotated[
        PositiveInt,
        Field(description='Кол-во коннектов превышающее pool_size',),
    ] = 10

    POSTGRES_POOL_SIZE: Annotated[
        PositiveInt,
        Field(description='Кол-во коннектов в пуле коннектов', ),
    ] = 5

    POSTGRES_POOL_PRE_PING: Annotated[
        bool,
        Field(description='Проверка коннекта перед каждым чекаутом',),
    ] = True

    POSTGRES_POOL_RECYCLE: Annotated[
        int,
        Field(
            AfterValidator(lambda v: max([-1, v,])),
            description='Закрывать коннект после n секунд неактивности.',
        ),
    ] = -1
