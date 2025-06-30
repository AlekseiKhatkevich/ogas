from prefect import flow, serve, task


@task
async def calculate_necessities() -> None:
    from center.usecases.operative_data import NecessityCalculationUseCase
    use_case = NecessityCalculationUseCase()
    await use_case.execute()


@task
async def calculate_manufacturing_plan() -> None:
    print('Calculating Manufacturing plan')


@flow(timeout_seconds=60 * 2, log_prints=True)
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
