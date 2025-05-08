import datetime

import ulid
from sqlalchemy import MetaData, TEXT, func
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
    }

    # noinspection PyNestedDecorators
    @declared_attr.directive
    @classmethod
    def __tablename__(cls) -> str:
        return cls.__name__.rstrip('ORM').lower()
