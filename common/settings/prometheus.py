import pathlib
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings


class PrometheusSettings(BaseSettings):
    PROMETHEUS_MULTIPROC_DIR: Annotated[
        pathlib.Path,
        Field(
            frozen=True,
            description='Prometheus использует для работы в многопроцессорном режиме.',
        )]
    PROMETHEUS_HTTP_SERVER_PORT: Annotated[
        int,
        Field(description='Порт сервера Prometheus.'),
    ] = 8001
