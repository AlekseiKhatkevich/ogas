import ulid
from pydantic import BaseModel, SecretStr

__all__ = (
    'KafkaHeader',
    'KafkaHeaders',
)


class KafkaHeader(BaseModel):
    token: SecretStr | None = None
    organization_id: ulid.ULID | None = None
    organization_name: str | None = None

    @property
    def auth_pair(self) -> dict[str, ulid.ULID | str] | None:
        if self.token is None or (self.organization_id is None and self.organization_name is None):
            return None
        else:
            return self.model_dump(exclude_none=True)


class KafkaHeaders(BaseModel):
    headers: list[KafkaHeader]
