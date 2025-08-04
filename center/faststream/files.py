import logfire
from faststream.nats import NatsRouter, ObjWatch
from faststream.nats.annotations import ObjectStorage
from nats.js.object_store import ObjectStore

from center.usecases.upload_file_via_sftp import UploadFileViaSFTPUseCase

__all__ = (
    'router',
)


router = NatsRouter(prefix='file_', )


@router.subscriber(
    'upload',
    obj_watch=ObjWatch(ignore_deletes=True),
)
async def file_upload_handler(
        filename: str,
        storage: ObjectStorage,
) -> None:
    file: ObjectStore.ObjectResult = await storage.get(filename)
    logfire.info(
        'Got a file',
        filename=filename,
        size=file.info.size,
        bucket=file.info.bucket,
        description=file.info.description,
    )

    use_case = UploadFileViaSFTPUseCase(file)
    await use_case.execute()
    await storage.delete(filename)
    logfire.info('File deleted', filename=filename)

