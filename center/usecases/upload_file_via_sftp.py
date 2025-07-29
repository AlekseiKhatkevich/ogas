import aiofiles
import asyncssh
from nats.js.object_store import ObjectStore

from common.usecases.common import AbstractUseCase


class UploadFileViaSFTPUseCase(AbstractUseCase):
    def __init__(self, file_obj: ObjectStore.ObjectResult):
        self.file_obj = file_obj

    async def execute(self):
        async with aiofiles.tempfile.NamedTemporaryFile(delete=True, delete_on_close=False) as temp_file:
            await temp_file.write(self.file_obj.data)
            await temp_file.flush()

            async with asyncssh.connect('localhost', username='sftpuser', password='1q2w3e') as conn:
                async with conn.start_sftp_client() as sftp:
                    await sftp.put(temp_file.name, remotepath=self.file_obj.info.name)


