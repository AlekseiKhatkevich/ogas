import asyncio
import math
from typing import Generator, Iterable, Iterator, Type

import more_itertools

import constants


def get_all_subclasses[T](base_cls: Type[T]) -> Generator[Type[T]]:
    """
    Получаем все субклассы класса и их субклассы тоже рекурсивно.
    """
    for subclass in base_cls.__subclasses__():
        yield subclass
        yield from get_all_subclasses(subclass)


def batch_for_asyncpg[T](iterable: Iterable[T], batch_size: int | None = None) -> Iterator[tuple[T, ...]]:
    """
    Для решения проблемы того, что в syncpg нельзя передать более 32767 аргументов. Делим датасет на батчи так,
    чтобы каждый имел менее 32767 аргументов.
    """
    safety_coefficient = 0.95

    if batch_size is None:
        head, iterable = more_itertools.spy(iterable)
        if not head:
            batch_size = 1
        else:
            try:
                num_elements = len(head[0])
            except TypeError:
                num_elements = len(head[0].__class__.model_fields)  # for pydantic
            batch_size = math.floor((constants.SMALLINT_MAX / num_elements) * safety_coefficient)

    yield from more_itertools.batched(iterable, batch_size)


class AsyncObj:
    def __init__(self, *args, **kwargs):
        """
        Standard constructor used for arguments pass
        Do not override. Use __ainit__ instead
        """
        self.storedargs = args, kwargs
        self.async_initialized = False

    async def __ainit__(self, *args, **kwargs):
        """ Async constructor, you should implement this """

    async def __initobj(self):
        """ Crutch used for __await__ after spawning """
        assert not self.async_initialized
        self.async_initialized = True
        await self.__ainit__(*self.storedargs[0], **self.storedargs[1])  # pass the parameters to __ainit__ that
        # passed to __init__
        return self

    def __await__(self):
        return self.__initobj().__await__()

    def __init_subclass__(cls, **kwargs):
        assert asyncio.iscoroutinefunction(cls.__ainit__)  # __ainit__ must be async

    @property
    def async_state(self):
        if not self.async_initialized:
            return "[initialization pending]"
        return "[initialization done and successful]"
