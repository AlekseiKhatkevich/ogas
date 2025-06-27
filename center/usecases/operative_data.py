from center.serializers import OperativeDataIn
from common.repositories.postgres import CommonPostgresRepository
from common.resources.database.redis import RedisDAO, redis_container
from common.usecases.common import AbstractUseCase
from utils.common import AsyncObj
from ..enums import Role
from ..orm_models import NecessityORM, OperativeDataORM, OrganizationORM
from ..repositories.postgres import (
    NecessityPostgresRepository,
    OperativeDataPostgresRepository,
    OrganizationStockPostgresRepository,
)


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
    def __init__(
            self,
            normal_level_hours: int = 24 * 2,
            repository: OrganizationStockPostgresRepository = OrganizationStockPostgresRepository,
            necessity_repository: NecessityPostgresRepository = NecessityPostgresRepository,
    ) -> None:
        # noinspection PyCallingNonCallable
        self.repository = repository()
        self.normal_level_hours = normal_level_hours
        # noinspection PyCallingNonCallable
        self.necessity_repository = necessity_repository()

    async def execute(self) -> None:
        prev_element = None
        async for element in self.repository.get_info_for_schedule():
            if prev_element is None:
                prev_element = element
                continue
            elif prev_element.product_id == element.product_id:
                await self.calculate([prev_element, element])
                prev_element = None
            else:
                await self.calculate([prev_element])
                prev_element = element

        else:
            if prev_element is not None:
                await self.calculate([prev_element])

    async def calculate(self, elements: list[OperativeDataIn]) -> NecessityORM | None:
        producer, consumer = self.get_consumer_and_producer(elements)
        necessity_instance = self.calculate_base_case(producer, consumer)
        if necessity_instance is not None:
            await self.necessity_repository.add_all([necessity_instance])
        return necessity_instance

    @staticmethod
    def get_consumer_and_producer(elements: list[OperativeDataIn]) \
            -> tuple[OperativeDataIn | None, OperativeDataIn | None]:
        producer = consumer = None
        for element in elements:
            if element.role == Role.PRODUCER:
                producer = element
            else:
                consumer = element

        return producer, consumer

    def calculate_base_case(
            self,
            producer: OperativeDataIn | None,
            consumer: OperativeDataIn | None,
    ) -> NecessityORM | None:
        if consumer is None:
            return None

        in_stock = consumer.in_stock
        cap_per_interval = consumer.capability_per_interval
        capability_interval = consumer.capability_interval
        min_level = consumer.min_level
        cons_per_hour = (
                consumer.cons_per_hour or cap_per_interval / capability_interval.to_hours
        )
        in_stock_at_producer = producer.in_stock if producer is not None else 0

        hours_to_min_level = max((in_stock - min_level), 0) / cons_per_hour
        hours_to_normal_level = max(self.normal_level_hours - hours_to_min_level, 0)
        necessity_to_normal_level = (cons_per_hour * hours_to_normal_level)
        to_produce = max(necessity_to_normal_level - in_stock_at_producer, 0)

        return NecessityORM(
            product_id=consumer.product_id,
            to_produce=to_produce,
            in_stock_at_consumer=in_stock,
            in_stock_at_producer=in_stock_at_producer,
        )

