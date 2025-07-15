from typing import Annotated

from pydantic import Field
from pydantic_settings import BaseSettings


class DistributedSettings(BaseSettings):
    KAFKA_DISTRIBUTED_SETTINGS_TOPIC_PREFIX: Annotated[
        str,
        Field(description='Префикс топика Кафки для распределенных сеттингов.'),
    ] = 'distributed_settings'
