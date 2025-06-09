from typing import TYPE_CHECKING

from faststream import Depends, apply_types

from center.faststream.dependencies import organization
from common.usecases.common import AbstractUseCase
from utils.common import AsyncObj

if TYPE_CHECKING:
    from center.serializers import OperativeDataIn
    from ..orm_models import OrganizationORM


class OperativeDataInSaveUseCase(AsyncObj, AbstractUseCase):

    @apply_types
    async def __ainit__(
            self, op_info: 'OperativeDataIn',
            current_organization: 'OrganizationORM' = Depends(organization),
    ) -> None:
        self.op_info = op_info
        self.current_organization = current_organization

    async def execute(self):
        pass
