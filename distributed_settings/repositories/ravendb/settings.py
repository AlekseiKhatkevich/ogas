from distributed_settings.repositories.ravendb import CommonRavenDBRepository
from distributed_settings.serializers.settings_out import SettingsOut

__all__ = (
    'SettingsRavenDBRepository',
)


class SettingsRavenDBRepository(CommonRavenDBRepository[SettingsOut]):
    _collection = 'settings'
    _object_type = SettingsOut
