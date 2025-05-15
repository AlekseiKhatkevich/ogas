from pydantic_settings import BaseSettings, SettingsConfigDict

from common.settings.common import CommonSettings
from common.settings.postgres import PostgresSettings

__all__ = (
    'general_settings',
)


class GeneralSettings(
    PostgresSettings,
    CommonSettings,
    BaseSettings,
):
    model_config = SettingsConfigDict(
        env_file=(
            'env/postgres.env',
            'env/.env',
        ),
        env_file_encoding='utf-8',
    )


# noinspection PyArgumentList
general_settings = GeneralSettings()
