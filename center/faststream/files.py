import tempfile

import asyncssh
import logfire
from faststream.nats import NatsRouter, ObjWatch
from faststream.nats.annotations import ObjectStorage

__all__ = (
    'router',
)


router = NatsRouter(prefix='file_', )


@router.subscriber(
    'upload',
    obj_watch=ObjWatch(declare=False, ignore_deletes=True),
)
async def handler(
        filename: str,
        storage: ObjectStorage,
) -> None:
    file = await storage.get(filename)
    logfire.info('Got a file', data=file.data)

    # todo  aio version
    with tempfile.NamedTemporaryFile(delete=True, delete_on_close=False) as temp_file:
        temp_file.write(file.data)
        temp_file.flush()

        async with asyncssh.connect('localhost', username='sftpuser', password='1q2w3e') as conn:
            async with conn.start_sftp_client() as sftp:
                await sftp.put(temp_file.name, remotepath=file.info.name)

        # await storage.delete(filename)


