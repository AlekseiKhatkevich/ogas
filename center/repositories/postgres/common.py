from abc import ABC
from typing import ClassVar, TYPE_CHECKING

from common.resources.database.postgres.database import Database, db

if TYPE_CHECKING:
    from common.resources.database.postgres.alchemy_related import Base

__all__ = (
    'AbstractPostgresRepository',
    'CommonPostgresRepository',
)


class AbstractPostgresRepository(ABC):
    _model: ClassVar['Base']

    def __init__(self, _db: Database = db, /, ) -> None:
        self._db = db


class CommonPostgresRepository[M:'Base'](AbstractPostgresRepository):
    def __init_subclass__(cls, model: M, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._model: M = model
