import math

from asyncstdlib import groupby

from center.repositories.postgres import NecessityPostgresRepository
from common.usecases.common import AbstractUseCase
from dataclasses import dataclass



class ManufacturingPlanUseCase(AbstractUseCase):
    # noinspection PyCallingNonCallable
    def __init__(
            self,
            plan_repository=None,
            necessity_repository: NecessityPostgresRepository = NecessityPostgresRepository,
    ) -> None:
        # self.plan_repository = plan_repository()
        self.necessity_repository = necessity_repository()

    async def execute(self):
        async for prodict_id, necessity_iter in groupby(
            self.necessity_repository.get_necessities_for_planing(),
            key=lambda n: n.product_id,
        ):
            plan = await self.calculate_plan(prodict_id, necessity_iter)

    async def calculate_plan(self, prodict_id, necessities):
        with_real_producers = [n async for n in necessities if not n.can_not_produce]
        if not with_real_producers:
            return
                    # все склады и импорт -> импорт

        common_cap_per_hour = math.fsum(r.capability_per_hour for r in with_real_producers)
        for info in with_real_producers:
            info.common_capacity_per_hour = common_cap_per_hour
        1+1

# round


