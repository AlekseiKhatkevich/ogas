from pathlib import Path

import aiofiles
import logfire
from nats.js.object_store import ObjectStore

from common.resources.ssh.sftp import ssh_repository
from common.usecases.common import AbstractUseCase


class UploadFileViaSFTPUseCase(AbstractUseCase):
    def __init__(self, file_obj: ObjectStore.ObjectResult):
        self.file_obj = file_obj

    @logfire.instrument('UploadFileViaSFTPUseCase')
    async def execute(self) -> None:
        async with aiofiles.tempfile.NamedTemporaryFile(delete=True, delete_on_close=False) as temp_file:
            await temp_file.write(self.file_obj.data)
            await temp_file.flush()
            logfire.info('Created tmp file', name=temp_file.name)

            async with ssh_repository.sftp_client as sftp:
                await sftp.put(
                    temp_file.name,
                    remotepath=Path(self.file_obj.info.name).name,
                    preserve=True,
                )
                logfire.info('File was sent via SFTP', _tags=['sftp'])
