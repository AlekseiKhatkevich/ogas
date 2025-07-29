from contextlib import asynccontextmanager
from typing import AsyncGenerator, TYPE_CHECKING

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
            yield conn.connection_lost()

    @property
    @asynccontextmanager
    async def sftp_client(self) -> AsyncGenerator['SFTPClient']:
        async with self.connection as connection:
            async with connection.start_sftp_client() as sftp:
                yield sftp


ssh_repository = SSHRepository(settings.SFTP_HOST, settings.SFTP_USERNAME, settings.SFTP_PASSWORD)
