import structlog
from faststream.kafka import KafkaRouter

from common import settings
from distributed_settings.serializers.settings_out import SettingsSerializer
from distributed_settings.usecases.settings_change import DistributedSettingsHandlingUseCase

log = structlog.get_logger()

router = KafkaRouter(prefix=f'{settings.KAFKA_DISTRIBUTED_SETTINGS_TOPIC_PREFIX}_')


@router.subscriber(settings.APP_NAME, title='settings-in')
async def fetch_and_apply_settings(settings_in: SettingsSerializer) -> None:
    await log.ainfo(f'Got settings from Kafka --  {settings_in}.')
    use_case = DistributedSettingsHandlingUseCase()
    use_case.in_place_reload(settings, settings_in.settings)
    await log.ainfo(f'Settings reloaded -- {settings}')
