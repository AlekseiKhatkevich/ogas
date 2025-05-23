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
