from distributed_settings.repositories.ravendb import CommonRavenDBRepository
from distributed_settings.serializers.settings_out import SettingsSerializer

__all__ = (
    'SettingsRavenDBRepository',
)


class SettingsRavenDBRepository(CommonRavenDBRepository[SettingsSerializer]):
    _collection = 'settings'
    _object_type = SettingsSerializer
