from typing import TYPE_CHECKING

from alembic.autogenerate import rewriter
from alembic.operations import ops
from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import Boolean, Enum, Integer, String, UUID

from common.orm_models.custom_types import ULID

if TYPE_CHECKING:
    from alembic.runtime.migration import MigrationContext

writer = rewriter.Rewriter()

one_byte_alignment_types = (String, Enum,)
four_byte_alignment_types = (Boolean, Integer,)
sixteen_byte_alignment_types = (ULID, UUID, )


@writer.rewrites(ops.CreateTableOp)
def order_columns(context: 'MigrationContext', revision: tuple, op: ops.CreateTableOp) -> ops.CreateTableOp:
    """
    https://www.cybertec-postgresql.com/en/type-alignment-padding-bytes-no-space-waste-in-postgresql/

    -- first, define all frequently accessed columns of type uuid: that data type has an alignment of one byte,
    but a fixed size of 16 bytes, so no padding bytes will be necessary

    -- next, define the columns with a data type with an alignment of eight bytes (bigint, timestamp, timestamp with
    time zone, double precision etc.)

    -- then, define the columns with a data type with an alignment of four bytes (integer, date, real etc.)

    -- then, define the columns with a data type with an alignment of two bytes (essentially, smallint)

    -- finally, define the columns with a data type with an alignment of one byte or with variable length (boolean,
    text, varchar, character, numeric, other uuid columns etc.)

    Суть - сортируем колонки в создаваемой таблице по убыванию выравнивания байт для экономии места.
    Пример взят отсюда  --
    https://alembic.sqlalchemy.org/en/latest/cookbook.html#apply-custom-sorting-to-table-columns-within-create-table
    """
    columns_with_weights = []
    for col in op.columns:
        if isinstance(col, Column):
            if isinstance(col.type, one_byte_alignment_types):
                weight = 1
            elif isinstance(col.type, four_byte_alignment_types):
                weight = 4
            elif isinstance(col.type, sixteen_byte_alignment_types):
                weight = 16
            else:
                raise NotImplementedError(f'Please add column type {col.type} as it is unknown for now.')

            columns_with_weights.append((weight, col.copy(),))

    columns = [
        col for _, col in sorted(columns_with_weights, key=lambda entry: entry[0], reverse=True)
    ]

    return ops.CreateTableOp(op.table_name, columns, schema=op.schema, **op.kw)
