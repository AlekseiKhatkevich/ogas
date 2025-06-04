
from typing import TYPE_CHECKING

from common.repositories.postgres import ProductPostgresRepository
from common.usecases.common import AbstractUseCase

if TYPE_CHECKING:
    from common.enums.product import ProductUnit
    from common.orm_models import ProductORM


class UpsertProductUseCase(AbstractUseCase):
    def __init__(self,
                 name: str,
                 unit: 'ProductUnit',
                 code: str,
                 categories: set[str],
                 *,
                 repository=ProductPostgresRepository,
                 ) -> None:
        self._repository = repository()
        self.name = name
        self.unit = unit
        self.code = code
        self.categories = categories

    async def execute(self) -> 'ProductORM':
        return await self._repository.create_or_update_product(self.name, self.unit, self.code, self.categories)
