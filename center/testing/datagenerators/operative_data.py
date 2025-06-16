import asyncio
import datetime
import random

import sqlalchemy as sa

from center.orm_models import OrganizationORM
from center.serializers import OperativeDataIn
from common.orm_models import ProductORM
from common.resources.database.postgres import db
from constants import ORGANIZATION_TEST_TOKEN
from faststream_serve import broker


def random_without_zero() -> int:
    return random.randint(-50, 10) or random_without_zero()


async def generate(limit: int = 9999999, sleep: float = 0.05):
    async with db.async_session as session:
        res = await session.scalars(
            sa.select(OrganizationORM.id)
        )
        organization_ids = res.all()
        res = await session.scalars(
            sa.select(ProductORM.id)
        )
        product_ids = res.all()

    counter = 0

    await broker.connect()

    while counter < limit:
        await asyncio.sleep(sleep)

        data = OperativeDataIn(
            product_id=random.choice(product_ids),
            diff=random_without_zero(),
            change_datetime=datetime.datetime.now(tz=datetime.UTC) - \
                            datetime.timedelta(seconds=random.randint(0, 60)),
        )
        organization_id = random.choice(organization_ids)

        await broker.publish(
            message=data,
            topic='operative_data_in',
            # no_confirm=True,
            headers={
                'content-type': 'application/json',
                'organization_id': str(organization_id),
                'token': ORGANIZATION_TEST_TOKEN,
            },
        )

        counter += 1
