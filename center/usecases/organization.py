import datetime
from typing import TYPE_CHECKING

from center.repositories.postgres import OrganizationPostgresRepository
from common.usecases.common import AbstractUseCase

if TYPE_CHECKING:
    from center.serializers import OrganizationUpdateIn
    from center.orm_models import OrganizationORM
    from faststream.kafka.publisher.asyncapi import AsyncAPIDefaultPublisher


class OrganizationUpdateUseCase(AbstractUseCase):
    def __init__(
            self,
            name: str,
            data: 'OrganizationUpdateIn',
            publisher: 'AsyncAPIDefaultPublisher',
            repository: OrganizationPostgresRepository = OrganizationPostgresRepository,
    ) -> None:
        self.name = name
        self.data = data
        self.publisher = publisher
        # noinspection PyCallingNonCallable
        self.repository = repository()

    async def execute(self) -> 'OrganizationORM':
        instance = await self.repository.update_organization(self.name, self.data)

        if instance is not None and instance.name != self.name:
            data_out = dict(
                old_name=self.name,
                new_name=instance.name,
                time=datetime.datetime.now(tz=datetime.UTC),
            )
            await self.publisher.publish(data_out)

        return instance
