from pydantic_settings import BaseSettings, SettingsConfigDict

from common.settings.common import CommonSettings
from common.settings.kafka import KafkaSettings
from common.settings.postgres import PostgresSettings

__all__ = (
    'general_settings',
    'GeneralSettings',
)


class GeneralSettings(
    PostgresSettings,
    KafkaSettings,
    CommonSettings,
    BaseSettings,
):
    model_config = SettingsConfigDict(
        env_file=(
            'env/postgres.env',
            'env/kafka.env',
            'env/.env',
        ),
        env_file_encoding='utf-8',
    )


# noinspection PyArgumentList
general_settings = GeneralSettings()
