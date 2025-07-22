from functools import partial

import logfire

from common.settings.general import general_settings as settings

__all__ = (
    'logfire_configure',
)

logfire_configure = partial(
    logfire.configure,
    environment=settings.ENVIRONMENT,
    service_name=settings.APP_NAME,
    token=settings.LOGFIRE_TOKEN,
    distributed_tracing=True,
)

