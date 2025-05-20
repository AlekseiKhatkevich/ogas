from typing import Annotated

from pydantic import AfterValidator, Field, KafkaDsn
from pydantic_settings import BaseSettings


class KafkaSettings(BaseSettings):
    KAFKA_DSN: Annotated[
        KafkaDsn,
        Field(repr=False, description='Урл Кафки.', ),
        AfterValidator(lambda v: f'{v.host}:{v.port}'),
    ]
