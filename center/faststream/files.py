import logfire
from faststream.nats import NatsRouter, ObjWatch
from faststream.nats.annotations import ObjectStorage

from center.usecases.upload_file_via_sftp import UploadFileViaSFTPUseCase

__all__ = (
    'router',
)


router = NatsRouter(prefix='file_', )


@router.subscriber(
    'upload',
    obj_watch=ObjWatch(ignore_deletes=True),
)
async def handler(
        filename: str,
        storage: ObjectStorage,
) -> None:
    file = await storage.get(filename)
    logfire.info('Got a file', data=file.data)

    use_case = UploadFileViaSFTPUseCase(file)
    await use_case.execute()
    await storage.delete(filename)


