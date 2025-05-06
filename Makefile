all: postgres_downgrade_db postgres_upgrade_db

down := -1
up := head

#  Накатывает миграции в postgres
postgres_upgrade_db:
	uv run alembic upgrade $(up)

# Откатывает 1 миграцию назад от текущей точки
postgres_downgrade_db:
	uv run alembic downgrade $(down)