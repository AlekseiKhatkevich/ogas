import dataclasses
from functools import cached_property

import ulid
from pydantic import BaseModel, SecretStr, TypeAdapter

from center.orm_models import OrganizationORM

__all__ = (
    'KafkaHeader',
    'AuthStatus',
    'kafka_header_list_adapter',
)


class KafkaHeader(BaseModel):
    token: SecretStr | None = None
    organization_id: ulid.ULID | None = None
    organization_name: str | None = None


@dataclasses.dataclass
class AuthStatus:
    header: KafkaHeader
    organization: OrganizationORM = None

    @cached_property
    def auth_pair(self) -> dict | None:
        if self.header.token is None or (self.header.organization_id is None and self.header.organization_name is None):
            return None
        else:
            return self.header.model_dump(exclude_none=True)

    @property
    def identifier(self) -> ulid.ULID | str:
        return self.header.organization_id or self.header.organization_name


kafka_header_list_adapter = TypeAdapter(list[KafkaHeader])
