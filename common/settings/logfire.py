from typing import Annotated, Self

from pydantic import Field, HttpUrl, model_validator
from pydantic_settings import BaseSettings


class LogfireSettings(BaseSettings):
    LOGFIRE_TOKEN: Annotated[
        str,
        Field(repr=False, description='Logfire write token',),
    ]
    OTEL_EXPORTER_OTLP_ENDPOINT: Annotated[
        HttpUrl | None,
        Field(description='Урл для подключения альтернативного бэкенда для Logfire')
    ] = None
    LOGFIRE_SEND_TO_LOGFIRE: Annotated[
        bool,
        Field(description='Нужно ли отсылать данные на бэкенд logfire.')
    ] = True

    @model_validator(mode='after')
    def switch_off_send_to_logfire(self) -> Self:
        """
        Если подключен внешний бэкенд – то не посылаем данные на дефолтный бекенд logfire.
        https://logfire.pydantic.dev/docs/how-to-guides/alternative-backends/#example-with-jaeger
        """
        if self.OTEL_EXPORTER_OTLP_ENDPOINT is not None:
            self.LOGFIRE_SEND_TO_LOGFIRE = False
        return self

