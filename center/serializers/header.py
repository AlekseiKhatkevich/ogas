import dataclasses

import ulid
from pydantic import BaseModel, SecretStr, TypeAdapter

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
    auth_passed: bool = False

    @property
    def auth_pair(self) -> dict[str, ulid.ULID | str] | None:
        if self.header.token is None or (self.header.organization_id is None and self.header.organization_name is None):
            return None
        else:
            return self.header.model_dump(exclude_none=True)


kafka_header_list_adapter = TypeAdapter(list[KafkaHeader])
