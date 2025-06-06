from typing import Annotated

from pydantic import BaseModel, Field, SecretStr

__all__ = (
    'OrganizationUpdateIn',
)


class OrganizationUpdateIn(BaseModel):
    new_name: Annotated[
        str | None,
        Field(description='Новое наименование компании.'),
    ] = None
    new_token: Annotated[
        SecretStr | None,
        Field(description='Новый токен.', min_length=24, max_length=72,),
    ] = None

