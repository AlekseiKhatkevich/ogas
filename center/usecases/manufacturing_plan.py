from asyncstdlib import groupby

from center.repositories.postgres import NecessityPostgresRepository
from common.usecases.common import AbstractUseCase


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
        record, *_ = with_real_producers
        to_produce = record.to_produce
        fact_time = record.fact_time

        cap_per_hour_each = {
            r.producer_id: r.capability / r.capability_interval.to_hours
            for r in with_real_producers
        }
        common_cap_per_hour = sum(cap_per_hour_each.values())
        # hours_to_produce = to_produce / common_cap_per_hour
        share_each = {
            producer_id: cap_per_hour / common_cap_per_hour
            for producer_id, cap_per_hour in cap_per_hour_each.items()
        }
        plan_each = {product_id: to_produce * share for product_id, share in share_each.items()}
# round


