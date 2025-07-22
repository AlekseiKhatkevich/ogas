import functools
from typing import Callable

import asyncpg
from prefect import flow, serve, task
from prefect.concurrency.asyncio import concurrency
from prefect.logging import get_run_logger

from prefect_flows import prefect_logfire


# python -m  prefect_flows.calculate_necessity


def retry_on(*exceptions) -> Callable:
    def _handler(task, task_run, state) -> bool:
        try:
            state.result()
        except tuple(*exceptions):
            return True
        else:
            return False
    return _handler


retry_on_db_failures = functools.partial(
    retry_on,
    ConnectionRefusedError,
    asyncpg.PostgresConnectionError,
)


@task(
    retries=6,
    retry_condition_fn=retry_on_db_failures,
    retry_delay_seconds=60 * 5,
    timeout_seconds=60 * 2,
)
@prefect_logfire.instrument(span_name='prefect_calculate_necessities')
async def calculate_necessities() -> None:
    from center.usecases.operative_data import NecessityCalculationUseCase
    use_case = NecessityCalculationUseCase()
    logger = get_run_logger()
    logger.info('Calculating Necessity')
    async with concurrency("database", occupy=1, strict=True):
        await use_case.execute()


@task(
    retries=6,
    retry_condition_fn=retry_on_db_failures,
    retry_delay_seconds=60 * 5,
    timeout_seconds=60 * 5,
)
@prefect_logfire.instrument(span_name='prefect_calculate_manufacturing_plan')
async def calculate_manufacturing_plan() -> None:
    from center.usecases.manufacturing_plan import ManufacturingPlanUseCase
    use_case = ManufacturingPlanUseCase()
    logger = get_run_logger()
    logger.info('Calculating Manufacturing plan')
    async with concurrency("database", occupy=1, strict=True):
        await use_case.execute()


@flow
@prefect_logfire.instrument(span_name='prefect_calc_necessities_and_plan')
async def calc_necessities_and_plan() -> None:
    await calculate_necessities()
    await calculate_manufacturing_plan()


calc_necessities_and_plan_deploy = calc_necessities_and_plan.to_deployment(
    name='calculate_necessities_an_plan',
    cron='0 * * * *',  # раз в час
    tags=['necessity', 'plan', 'OGAS', ],
    description='Рассчитывает необходимость в продукте, пишет ее в БД, затем считает план пр-ва.',
    version='0.0.11',
)

if __name__ == '__main__':
    serve(calc_necessities_and_plan_deploy, )
