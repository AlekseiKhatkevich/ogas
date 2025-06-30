import functools
from typing import Callable

import asyncpg
from prefect import flow, serve, task


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
async def calculate_necessities() -> None:
    from center.usecases.operative_data import NecessityCalculationUseCase
    use_case = NecessityCalculationUseCase()
    await use_case.execute()


@task
async def calculate_manufacturing_plan() -> None:
    print('Calculating Manufacturing plan')


@flow(
    log_prints=True,
)
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
