"""Create procedure for GOST

Revision ID: 27c12e6b1122
Revises: 08f1c3b6ca7d
Create Date: 2025-05-12 12:15:19.673131

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import common.orm_models.custom_types


# revision identifiers, used by Alembic.
revision: str = '27c12e6b1122'
down_revision: Union[str, None] = '08f1c3b6ca7d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


procedure_sql = """
CREATE OR REPLACE PROCEDURE import_national_standards()
LANGUAGE plpgsql
AS $$
BEGIN
    SET LOCAL statement_timeout = '60s';

    DROP TABLE IF EXISTS tmp;

    CREATE TEMPORARY TABLE tmp (
        code text,
        description text,
        is_active text,
        oks_code text
    );

COPY tmp (code, description, is_active, oks_code)
FROM PROGRAM 'curl -L -m 10 --compressed  https://www.rst.gov.ru/opendata/7706406291-nationalstandards/data-20240808-structure-20220330.csv'
WITH
    delimiter ';'
    csv
    header
    encoding 'windows-1251'
;

WITH tmp_transformed AS (
    SELECT
        code,
        description,
        CASE
            WHEN lower(is_active) IN ('принят', 'действует') THEN TRUE
            ELSE FALSE
        END AS is_active,
        string_to_array(oks_code, ';') AS oks_code
    FROM tmp
)
MERGE INTO standard
USING tmp_transformed
ON tmp_transformed.code = standard.code
WHEN MATCHED AND (
        standard.description != tmp_transformed.description OR
        standard.is_active != tmp_transformed.is_active OR
        standard.oks_code != tmp_transformed.oks_code
    ) THEN
    UPDATE SET
        description = tmp_transformed.description,
        is_active = tmp_transformed.is_active,
        oks_code = tmp_transformed.oks_code,
        updated_at = now()
WHEN NOT MATCHED THEN
    INSERT (code, description, is_active, oks_code) VALUES (
        tmp_transformed.code,
        tmp_transformed.description,
        tmp_transformed.is_active,
        tmp_transformed.oks_code
    )
    ;
    -- Drop the temporary table
    DROP TABLE IF EXISTS tmp;
END;
$$;
"""


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(procedure_sql)


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP PROCEDURE IF EXISTS import_national_standards')
