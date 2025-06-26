import asyncio
from collections import deque

from center.serializers import OperativeDataIn
from common.repositories.postgres import CommonPostgresRepository
from common.resources.database.redis import RedisDAO, redis_container
from common.usecases.common import AbstractUseCase
from utils.common import AsyncObj
from ..enums import Role
from ..orm_models import OperativeDataORM, OrganizationORM
from ..repositories.postgres import OperativeDataPostgresRepository, OrganizationStockPostgresRepository


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
    def __init__(self, repository: OrganizationStockPostgresRepository = OrganizationStockPostgresRepository, ) -> None:
        self.repository = repository()
        self.queue = deque(maxlen=2)

    async def execute(self):
        data_pipeline = self.repository.get_info_for_schedule()
        prev_element = None
        async for element in data_pipeline:
            if prev_element is None:
                prev_element = element
                continue
            elif prev_element.product_id == element.product_id:
                await self.calculate_regular_demand([prev_element, element])
                prev_element = None
            else:
                await self.calculate_demand_for_case_without_producer(prev_element)
                prev_element = element

        else:
            if prev_element is not None:
                await self.calculate_demand_for_case_without_producer(prev_element)

    async def calculate_regular_demand(self, elements):
        producer = consumer = None
        for element in elements:
            if element.role == Role.PRODUCER:
                producer = element
            else:
                consumer = element

        



    async def calculate_demand_for_case_without_producer(self, element):
        pass
