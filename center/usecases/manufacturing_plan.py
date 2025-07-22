import asyncio
import math
from typing import AsyncIterator, TYPE_CHECKING
from weakref import WeakKeyDictionary

import logfire
import ulid
from asyncstdlib import groupby

from pydantic_core import to_jsonable_python

from center.orm_models import PlanORM
from center.repositories.postgres import NecessityPostgresRepository, PlanPostgresRepository
from common.usecases.common import AbstractUseCase
from faststream_serve import broker

if TYPE_CHECKING:
    from common.repositories.postgres import InfoForPlanning
    from faststream.kafka import KafkaBroker


class ManufacturingPlanUseCase(AbstractUseCase):
    """
    https://stackoverflow.com/questions/66724841/using-a-semaphore-with-asyncio-in-python
    """
    # noinspection PyCallingNonCallable
    def __init__(
            self,
            plan_repository: PlanPostgresRepository = PlanPostgresRepository,
            necessity_repository: NecessityPostgresRepository = NecessityPostgresRepository,
            insert_concurrency: int = 10,
            insert_and_sent_timeout_sec: int = 5
    ) -> None:
        self.plan_repository = plan_repository()
        self.necessity_repository = necessity_repository()
        self._background_tasks = WeakKeyDictionary()
        self.semaphore = asyncio.Semaphore(insert_concurrency)
        self.insert_and_sent_timeout_sec = insert_and_sent_timeout_sec
        self._broker = broker

    async def save_in_db(self, plan: list[PlanORM], prodict_id: ulid.ULID) -> None:
        try:
            async with asyncio.timeout(self.insert_and_sent_timeout_sec), asyncio.TaskGroup() as tg:
                tg.create_task(self.plan_repository.add_all(plan))
                tg.create_task(self.send_to_kafka(plan))
        finally:
            self.semaphore.release()
            #  _background_tasks чиститься за счет слабых ссылок
            #  (prodict_id нужен, хоть и не используется напрямую)

    async def get_broker(self) -> 'KafkaBroker':
        # noinspection PyProtectedMember
        if self._broker._connection is None:
            await self._broker.connect()
        return self._broker

    @logfire.instrument()
    async def send_to_kafka(self, plan: list[PlanORM]) -> None:
        topic_prefix = 'plan_out_'
        for individual_plan in plan:
            if (org_id := individual_plan.organization_id) is None:
                topic = topic_prefix + 'import'
            else:
                topic = topic_prefix + str(org_id)
            message = to_jsonable_python(
                individual_plan.to_dict(exclude=['created_at', 'id', ]),
                serialize_unknown=True,
            )
            broker_inst = await self.get_broker()
            logfire.info(
                'Sending plan to kafka...',
                _tags=['plan', 'kafka', 'out'],
                message=message,
            )
            await broker_inst.publish(message, topic)

    async def execute(self) -> None:
        async for prodict_id, necessity_iter in groupby(
                self.necessity_repository.get_necessities_for_planing(),
                key=lambda n: n.product_id,
        ):
            await self.semaphore.acquire()
            plan = await self.calculate_plan(prodict_id, necessity_iter)
            write_plan_and_send_to_kafka_task = asyncio.create_task(self.save_in_db(plan, prodict_id))
            self._background_tasks[prodict_id] = write_plan_and_send_to_kafka_task

        for coro in asyncio.as_completed(self._background_tasks.values()):
            try:
                await coro
            except Exception as exc:
                print(f'We have an exception {exc}! Surprise motherfucker!!')

    @staticmethod
    async def calculate_plan(
            product_id: ulid.ULID,
            necessities: AsyncIterator['InfoForPlanning'],
    ) -> list[PlanORM]:
        necessities = [n async for n in necessities]
        with_real_producers = [n for n in necessities if not n.can_not_produce]
        if not with_real_producers:  # импорт
            instance = PlanORM(
                product_id=product_id,
                value=necessities[0].to_produce,
                fact_time=necessities[0].fact_time,
            )
            return [instance, ]

        common_cap_per_hour = math.fsum(r.capability_per_hour for r in with_real_producers)
        for info in with_real_producers:
            info.common_capacity_per_hour = common_cap_per_hour

        return [
            PlanORM(
                organization_id=info.producer_id,
                product_id=info.product_id,
                value=info.plan,
                fact_time=info.fact_time,
            ) for info in with_real_producers
        ]
