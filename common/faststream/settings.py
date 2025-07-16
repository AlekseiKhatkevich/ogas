from faststream.kafka import KafkaRouter
from faststream.kafka.annotations import KafkaMessage

from common import settings
from distributed_settings.serializers.settings_out import SettingsSerializer

router = KafkaRouter(prefix=f'{settings.KAFKA_DISTRIBUTED_SETTINGS_TOPIC_PREFIX}_')


@router.subscriber(
    settings.APP_NAME, title='settings-in',
    # group_id='settings_group',
    # auto_commit=False,
    # no_ack=True,
    # auto_offset_reset='earliest'
)
async def fetch_and_apply_settings(settings_in: SettingsSerializer, msg: KafkaMessage) -> None:
    print(f'Got settings {settings_in}')

    # комиитить предыдущий оффсет