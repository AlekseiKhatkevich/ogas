from typing import TYPE_CHECKING

from faststream import apply_types

from center.faststream.dependencies import CurrentOrganizationDep
from center.repositories.postgres import OrganizationStockPostgresRepository
from common.usecases.common import AbstractUseCase
from utils.common import AsyncObj

if TYPE_CHECKING:
    from center.serializers import OrganizationStockIn


class OrganizationStockSaveUseCase(AsyncObj, AbstractUseCase):
    @apply_types
    async def __ainit__(
            self,
            stock: 'OrganizationStockIn',
            current_organization: CurrentOrganizationDep,
    ):
        self.stock = stock
        self.current_organization = current_organization
        self.repository = OrganizationStockPostgresRepository()

    async def execute(self):
        await self.repository.insert_stock(self.stock, self.current_organization)
