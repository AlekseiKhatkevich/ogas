from typing import Annotated

from pydantic import AfterValidator, Field, KafkaDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    KAFKA_DSN: Annotated[
        KafkaDsn,
        Field(repr=False, description='Урл Кафки.', ),
        AfterValidator(lambda v: f'{v.host}:{v.port}'),
    ]
    model_config = SettingsConfigDict(
        env_file=(
            'env/kafka.env',
        ),
        env_file_encoding='utf-8',
    )
