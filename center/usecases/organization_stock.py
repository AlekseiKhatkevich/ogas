from typing import TYPE_CHECKING

from fast_depends import Depends
from faststream import apply_types

from center.faststream.dependencies import CurrentOrganizationDep, organization
from center.orm_models import OrganizationORM
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

    async def execute(self):
        1+1
        pass
