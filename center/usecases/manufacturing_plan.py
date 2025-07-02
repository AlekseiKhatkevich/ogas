from center.repositories.postgres import NecessityPostgresRepository
from common.usecases.common import AbstractUseCase
from asyncstdlib import groupby


class ManufacturingPlanUseCase(AbstractUseCase):
    # noinspection PyCallingNonCallable
    def __init__(
            self,
            plan_repository=None,
            necessity_repository: NecessityPostgresRepository = NecessityPostgresRepository,
    ) -> None:
        self.plan_repository = plan_repository()
        self.necessity_repository = necessity_repository()

    async def execute(self):
        async for prodict_id, necessity_iter in groupby(
                self.necessity_repository.get_necessities_for_planing()
        ):
            necessity_data = [necessity async for necessity in necessity_iter]


