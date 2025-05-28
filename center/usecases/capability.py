from typing import TYPE_CHECKING

from center.repositories.postgres import (
    CapabilityPostgresRepository,
    CommonPostgresRepository,
    UpsertResult,
)

from common.usecases.common import AbstractUseCase

if TYPE_CHECKING:
    from center.serializers import CapabilityIn


class UpdateCapabilitiesUseCase(AbstractUseCase):
    """
    Принимает данные о производительностях от компании и записывает их в БД.
    """
    def __init__(
            self,
            capabilities: set['CapabilityIn'],
            repository: CommonPostgresRepository = CapabilityPostgresRepository,
    ) -> None:
        self.capabilities = capabilities
        # noinspection PyCallingNonCallable
        self.repository = repository()

    async def execute(self) -> UpsertResult:
        return await self.repository.insert_or_update_capabilities(self.capabilities)
