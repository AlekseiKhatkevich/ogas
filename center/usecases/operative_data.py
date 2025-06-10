from faststream import Depends, apply_types

from center.faststream.dependencies import organization
from center.serializers import OperativeDataIn
from common.resources.database.redis import RedisDAO, redis_container
from common.usecases.common import AbstractUseCase
from utils.common import AsyncObj
from ..orm_models import OrganizationORM


class OperativeDataInSaveUseCase(AsyncObj, AbstractUseCase):
    @apply_types
    async def __ainit__(
            self,
            op_info: list[OperativeDataIn],
            current_organization: OrganizationORM = Depends(organization),
    ) -> None:
        self.op_info = op_info
        self.current_organization = current_organization
        self.redis_client = redis_container.get(RedisDAO)

    async def execute(self):
        pass
