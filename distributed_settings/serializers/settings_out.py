import datetime
from typing import Annotated, Any

from pydantic import AfterValidator, BaseModel, ConfigDict, Field


class MetadataOut(BaseModel):
    collection: Annotated[
        str,
        Field(alias='@collection', description='Наименование коллекции.'),
    ]
    change_vector: Annotated[
        str,
        Field(alias='@change-vector', description='Версия вектора.'),
    ]
    id: Annotated[
        str,
        Field(alias='@id', description='ID записи.'),
    ]
    last_modified: Annotated[
        datetime.datetime,
        Field(alias='@last-modified', description='Время создания/изменения.'),
    ]

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore',
    )


class SettingsOut(BaseModel):
    app: Annotated[
        str,
        Field(AfterValidator(lambda v: v.lower()), description='Название аппа.',)
    ]
    settings: Annotated[
        dict[str, Any],
        Field(description='Настройки.'),
    ]
    metadata: Annotated[
        MetadataOut,
        Field(alias='@metadata', description='Метадата из RavenDB.')
    ]

    model_config = ConfigDict(
        from_attributes=True,
        extra='ignore',
    )
