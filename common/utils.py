from typing import Generator, Type, TypeVar

T = TypeVar('T')


def get_all_subclasses(base_cls: Type[T]) -> Generator[Type[T]]:
    """
    Получаем все субклассы класса и их субклассы тоже рекурсивно.
    """
    for subclass in base_cls.__subclasses__():
        yield subclass
        yield from get_all_subclasses(subclass)
