import asyncio
import pathlib
from functools import cached_property
from typing import Any

from dotenv import load_dotenv
from pydantic.fields import FieldInfo, PrivateAttr
from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, SettingsConfigDict

from common.settings.common import CommonSettings
from common.settings.distributed_settings import DistributedSettings
from common.settings.kafka import KafkaSettings
from common.settings.logfire import LogfireSettings
from common.settings.postgres import PostgresSettings
from common.settings.prometheus import PrometheusSettings
from common.settings.ravendb import RavenDBSettings
from common.settings.redis import RedisSettings

__all__ = (
    'general_settings',
    'GeneralSettings',
)


def _load_all_envs() -> None:
    path = pathlib.Path('env/')
    for file in path.glob('*.env'):
        load_dotenv(file)


class KafkaSettingsSource(PydanticBaseSettingsSource):
    """Получаем настойки из кафки из последнего сообщения в очереди."""

    @cached_property
    def _last_settings_from_kafka(self) -> dict[str, str]:
        from common.resources.database.kafka.aio import kafka_broker
        try:

            try:
                loop = asyncio.get_event_loop()
            except RuntimeError as e:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            settings_ser = loop.run_until_complete(kafka_broker.fetch_last_message())
        finally:
            loop.close()

        return settings_ser.settings if settings_ser is not None else {}
        # return {}

    def get_field_value(self, field: FieldInfo, field_name: str) -> tuple[Any, str, bool]:
        return self._last_settings_from_kafka.get(field_name), field_name, False

    def __call__(self) -> dict[str, Any]:
        d: dict[str, Any] = {}

        #  Если так GeneralSettings(_no_kafka_source=True), то пропускаем получение сеттингов из Кафки.
        if self.current_state.get('_no_kafka_source', False):
            return d

        for field_name, field in self.settings_cls.model_fields.items():
            field_value, field_key, value_is_complex = self.get_field_value(
                field, field_name
            )
            field_value = self.prepare_field_value(
                field_name, field, field_value, value_is_complex
            )
            if field_value is not None:
                d[field_key] = field_value

        return d


class GeneralSettings(
    RavenDBSettings,
    RedisSettings,
    PostgresSettings,
    KafkaSettings,
    CommonSettings,
    PrometheusSettings,
    DistributedSettings,
    LogfireSettings,
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
            'env/logfire.env',
        ),
        env_file_encoding='utf-8',
        extra='ignore',
        env_ignore_empty=True,
    )
    _no_kafka_source: bool = PrivateAttr(default=False)

    @classmethod
    def settings_customise_sources(
            cls,
            settings_cls: type[BaseSettings],
            init_settings: PydanticBaseSettingsSource,
            env_settings: PydanticBaseSettingsSource,
            dotenv_settings: PydanticBaseSettingsSource,
            file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            KafkaSettingsSource(settings_cls),
            env_settings,
            dotenv_settings,
            file_secret_settings,
        )


# noinspection PyArgumentList
general_settings = GeneralSettings()
# _load_all_envs()
