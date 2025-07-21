from functools import partial

import logfire

from common.settings.general import general_settings as settings

__all__ = (
    'logfire_configure',
)

logfire_configure = partial(logfire.configure, environment=settings.ENVIRONMENT)

