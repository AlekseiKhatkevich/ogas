from functools import partial
import os

import logfire

from common.settings.general import general_settings as settings

__all__ = (
    'logfire_configure',
)


def _configure_and_export(**kwargs) -> logfire.Logfire:
    if (ep := settings.OTEL_EXPORTER_OTLP_ENDPOINT) is not None:
        os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = ep.unicode_string()
    return logfire.configure(**kwargs)


logfire_configure = partial(
    _configure_and_export,
    environment=settings.ENVIRONMENT,
    service_name=settings.APP_NAME,
    token=settings.LOGFIRE_TOKEN,
    distributed_tracing=True,
)
