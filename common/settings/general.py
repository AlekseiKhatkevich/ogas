from pydantic_settings import BaseSettings, SettingsConfigDict

from common.settings.common import CommonSettings
from common.settings.kafka import KafkaSettings
from common.settings.postgres import PostgresSettings
from common.settings.prometheus import PrometheusSettings
from common.settings.ravendb import RavenDBSettings
from common.settings.redis import RedisSettings

__all__ = (
    'general_settings',
    'GeneralSettings',
)


class GeneralSettings(
    RavenDBSettings,
    RedisSettings,
    PostgresSettings,
    KafkaSettings,
    CommonSettings,
    PrometheusSettings,
    BaseSettings,
):
    model_config = SettingsConfigDict(
        env_file=(
            'env/redis.env',
            'env/postgres.env',
            'env/kafka.env',
            'env/.env',
            'env/prometheus.env',
            'env/ravendb.env',
        ),
        env_file_encoding='utf-8',
        extra='ignore',
    )


# noinspection PyArgumentList
general_settings = GeneralSettings()
