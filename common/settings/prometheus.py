import pathlib
from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings


class PrometheusSettings(BaseSettings):
    PROMETHEUS_MULTIPROC_DIR: Annotated[
        pathlib.Path,
        Field(
            description='Prometheus использует для работы в многопроцессорном режиме.',
        )]
