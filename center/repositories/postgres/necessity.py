from center.orm_models import NecessityORM
from common.repositories.postgres import CommonPostgresRepository
import sqlalchemy as sa


__all__ = (
    'NecessityPostgresRepository',
)


class NecessityPostgresRepository(CommonPostgresRepository, model=NecessityORM):


    async def get_necessities_for_planing(self):
        stmt = sa.select(
            self._model.product_id,
            self._model.to_produce,
            self._model.created_at.label('fact_time'),
            # ...
        ).outerjoin(
            self._model.capabilities
        )
