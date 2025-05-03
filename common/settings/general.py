
__all__ = (
    'general_settings',
)

from pydantic_settings import BaseSettings, SettingsConfigDict

from common.settings.postgres import PostgresSettings


class GeneralSettings(
    PostgresSettings,
    BaseSettings,
):
    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


general_settings = GeneralSettings()
