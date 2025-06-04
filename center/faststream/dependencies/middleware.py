from typing import Any, Awaitable, Callable

from center.faststream.dependencies import current_organization_name

__all__ = (
    'current_organization_topic_middleware',
)


async def current_organization_topic_middleware(
    call_next: Callable[..., Awaitable[Any]],
    msg: Any,
    **options: Any,
) -> Any:
    """
    Для publisher.
    Добавляет к названию топика название текущей организации в конец.
    """
    options['topic'] = f'{options['topic']}_{current_organization_name.get()}'
    return await call_next(msg, **options)
