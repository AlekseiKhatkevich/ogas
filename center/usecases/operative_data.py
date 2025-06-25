import itertools

from center.serializers import OperativeDataIn
from common.repositories.postgres import CommonPostgresRepository, InfoForSchedule
from common.resources.database.redis import RedisDAO, redis_container
from common.usecases.common import AbstractUseCase
from utils.common import AsyncObj
from ..enums import Role
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


class PlanCalculationUseCase(AbstractUseCase):
    def __init__(self, data: tuple[InfoForSchedule, ...]) -> None:
        self.data = data

    async def execute(self):
        for product_id, product_data in itertools.groupby(self.data, lambda d: d.product_id):
            for data in product_data:
                producer_data = consumer_data = None
                if data.role == Role.PRODUCER:
                    producer_data = data
                elif data.role == Role.CONSUMER:
                    consumer_data = data
