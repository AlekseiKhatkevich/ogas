from faststream import Depends, apply_types

from center.faststream.dependencies import organization
from center.serializers import OperativeDataIn
from common.repositories.postgres import CommonPostgresRepository
from common.resources.database.redis import RedisDAO, redis_container
from common.usecases.common import AbstractUseCase
from utils.common import AsyncObj
from ..orm_models import OperativeDataORM, OrganizationORM
from ..repositories.postgres import OperativeDataPostgresRepository


class OperativeDataInSaveUseCase(AsyncObj, AbstractUseCase):
    @apply_types
    async def __ainit__(
            self,
            op_info: list[OperativeDataIn],
            current_organization: OrganizationORM = Depends(organization),
            repository: CommonPostgresRepository = OperativeDataPostgresRepository,
    ) -> None:
        self.op_info = op_info
        self.current_organization = current_organization
        self.redis_client = redis_container.get(RedisDAO)
        # noinspection PyCallingNonCallable
        self.repository = repository()

    async def execute(self) -> list[OperativeDataORM]:
        return await self.repository.insert_data(self.op_info, self.current_organization.id)
