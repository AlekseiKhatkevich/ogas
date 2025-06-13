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
        to_insert = []
        for info, org in zip(self.op_info, self.current_organizations):
            if org is not None:
                info.organization_id = org.id
                to_insert.append(info)
        return await self.repository.insert_data(to_insert)
