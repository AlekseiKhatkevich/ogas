import datetime
import enum
from typing import Any, Container, Iterable, Literal

import ulid
from sqlalchemy import MetaData, TEXT, func, inspect
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.orm import DeclarativeBase, declared_attr, mapped_column
from typing_extensions import Annotated

from common.orm_models.custom_types import ULID as ULID_TYPE_FIELD

ULID_PK = Annotated[
    ulid.ULID,
    mapped_column(
        primary_key=True,
        server_default=func.gen_monotonic_ulid(),
        comment='Primary key :: ULID.',
    ),]


class Base(AsyncAttrs, DeclarativeBase):
    is_view = False
    metadata = MetaData(naming_convention={
        'ix': 'ix_%(column_0_label)s',
        'uq': 'uq_%(table_name)s_%(column_0_name)s',
        'ck': 'ck_%(table_name)s_%(constraint_name)s',
        'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
        'pk': 'pk_%(table_name)s',
    })
    type_annotation_map = {
        datetime.datetime: postgresql.TIMESTAMP(timezone=True),
        datetime.time: postgresql.TIME(timezone=True),
        str: TEXT,
        ulid.ULID: ULID_TYPE_FIELD,  # pgx_ulid
        list[str]: MutableList.as_mutable(postgresql.ARRAY(TEXT)),
        enum.Enum: postgresql.ENUM(validate_strings=True),
        Literal: postgresql.ENUM(validate_strings=True),
    }

    # noinspection PyNestedDecorators
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.rstrip('ORM').lower()

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return NotImplemented
        return self.pk_values == other.pk_values

    @property
    def pk_values(self) -> list[Any]:
        primary_key = inspect(self.__class__).primary_key
        return [getattr(self, key.name) for key in primary_key]

    def to_dict(self, include: Iterable[str] | None = None, exclude: Iterable[str] | None = None) -> dict[str, Any]:
        data = {column.name: getattr(self, column.name) for column in self.__table__.columns}

        if include:
            return {key: data[key] for key in include if key in data}
        if exclude:
            return {key: value for key, value in data.items() if key not in exclude}

        return data
