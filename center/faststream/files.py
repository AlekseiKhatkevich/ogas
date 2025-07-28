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
    await storage.delete(filename)