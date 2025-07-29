from contextlib import asynccontextmanager
from functools import cache
from typing import Any, AsyncGenerator, TYPE_CHECKING

import asyncssh

from common import settings

if TYPE_CHECKING:
    from asyncssh import SFTPClient, SSHClientConnection


__all__ = (
    'ssh_repository',
    'SSHRepository',
)


class SSHRepository:
    def __init__(self, host: str, username: str, password: str) -> None:
        self.host = host
        self.username = username
        self.password = password

    @property
    @asynccontextmanager
    async def connection(self) -> AsyncGenerator['SSHClientConnection']:
        async with asyncssh.connect(self.host, username=self.username, password=self.password) as conn:
            yield conn

    @property
    @asynccontextmanager
    async def sftp_client(self) -> AsyncGenerator['SFTPClient']:
        async with self.connection as connection:
            async with connection.start_sftp_client() as sftp:
                yield sftp


ssh_repository: SSHRepository


@cache
def _get_ssh_repository() -> SSHRepository:
    return SSHRepository(settings.SFTP_HOST, settings.SFTP_USERNAME, settings.SFTP_PASSWORD.get_secret_value())


def __getattr__(name: str) -> Any:
    if name == 'ssh_repository':
        return _get_ssh_repository()
    elif name in __all__:
        import importlib
        return importlib.import_module('.' + name, __name__)
    else:
        raise AttributeError(f'module {__name__!r} has no attribute {name!r}')

