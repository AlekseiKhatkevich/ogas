import asyncio
import math
from typing import AsyncIterator, TYPE_CHECKING

import ulid
from asyncstdlib import groupby

from center.orm_models import PlanORM
from center.repositories.postgres import NecessityPostgresRepository, PlanPostgresRepository
from common.repositories.postgres import InfoForPlanning
from common.usecases.common import AbstractUseCase

if TYPE_CHECKING:
    from common.repositories.postgres import InfoForPlanning


class ManufacturingPlanUseCase(AbstractUseCase):
    # noinspection PyCallingNonCallable
    def __init__(
            self,
            plan_repository: PlanPostgresRepository = PlanPostgresRepository,
            necessity_repository: NecessityPostgresRepository = NecessityPostgresRepository,
            insert_concurrency: int = 10,
    ) -> None:
        self.plan_repository = plan_repository()
        self.necessity_repository = necessity_repository()
        self.insert_concurrency = insert_concurrency
        self._background_tasks = set()
        self.sem = asyncio.Semaphore(self.insert_concurrency)

    def _cleanup_after_insert(self, future):
        self._background_tasks.discard(future)
        self.sem.release()

    async def execute(self) -> None:
        async for prodict_id, necessity_iter in groupby(
            self.necessity_repository.get_necessities_for_planing(),
            key=lambda n: n.product_id,
        ):
            plan = await self.calculate_plan(prodict_id, necessity_iter)
            await self.sem.acquire()
            plan_insert_task = asyncio.create_task(self.plan_repository.add_all(plan))
            self._background_tasks.add(plan_insert_task)
            plan_insert_task.add_done_callback(self._cleanup_after_insert)
            await plan_insert_task

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
            return [instance,]

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


