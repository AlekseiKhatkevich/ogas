from faststream.kafka import KafkaRouter

from common import settings
from distributed_settings.serializers.settings_out import SettingsSerializer

router = KafkaRouter(prefix=f'{settings.KAFKA_DISTRIBUTED_SETTINGS_TOPIC_PREFIX}_')


@router.subscriber(settings.APP_NAME, title='settings-in')
async def fetch_and_apply_settings(settings_in: SettingsSerializer) -> None:
    print(f'Got settings {settings_in}')
    print(settings.PROMETHEUS_MULTIPROC_DIR)
