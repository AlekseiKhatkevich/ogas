import functools
import operator
from typing import Any, Callable, TYPE_CHECKING, Type

if TYPE_CHECKING:
    from pydantic import BaseModel


def hashable_model[T: 'BaseModel'](fields: list[str]) -> Callable[[Type[T]], Type[T]]:
    """
    Делает модель pydantic хешируемой по набору полей.
    """
    @functools.wraps(hashable_model)
    def decorator(cls: Type[T]) -> Type[T]:

        def __hash__(self) -> int:
            return functools.reduce(operator.xor, (hash(getattr(self, field)) for field in fields))

        def __eq__(self, other: Any) -> bool:
            if not isinstance(other, cls):
                return NotImplemented
            return all(getattr(self, field) == getattr(other, field) for field in fields)

        cls.__hash__ = __hash__
        cls.__eq__ = __eq__

        return cls

    return decorator
