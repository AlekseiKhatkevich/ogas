from prefect import flow, serve
from sqlalchemy import text


@flow(retries=12, retry_delay_seconds=60)
async def import_gosts():
    """
    Импорт данных из внешнего CSV файла в модель standard.
    uv run flows/import_gosts.py
    """
    from common.resources.database.postgres import db

    async with db.async_session as session:
        await session.execute(
            text('CALL import_national_standards();')
        )
        await session.commit()


if __name__ == '__main__':
    import_gosts_deploy = import_gosts.to_deployment(
        name='import_gosts',
        cron='0 14 * * *',
        tags=['import', 'csv', 'OGAS', ],
        description='Скачивает и помещает в БД данные о ГОСТах',
        version='0.0.11',
    )
    serve(import_gosts_deploy, )
