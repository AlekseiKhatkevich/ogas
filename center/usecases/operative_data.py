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
    async def __ainit__(
            self,
            op_info: list[OperativeDataIn],
            current_organizations: list[OrganizationORM | None],
            repository: CommonPostgresRepository = OperativeDataPostgresRepository,
    ) -> None:
        self.op_info = op_info
        self.current_organizations = current_organizations
        self.redis_client = redis_container.get(RedisDAO)
        # noinspection PyCallingNonCallable
        self.repository = repository()

    async def execute(self) -> list[OperativeDataORM]:
        for info, org in zip(self.op_info, self.current_organizations):
            info.organization_id = org.id
        return await self.repository.insert_data(self.op_info,)
