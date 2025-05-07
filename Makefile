SHELL := /bin/bash
.PHONY: all
.DEFAULT_GOAL := help

#all: install_packages_dev

postgres_downgrade_db: down = -1
postgres_upgrade_db: up = head

help:  ## help as usual
	uvx --no-cache --no-progress --from rich-cli rich README.md --theme monokai --hyperlinks --pager

postgres_migration:  ## Создает файл миграции с изменениями в моделях
	uv run alembic revision --autogenerate -m "$(message)"

postgres_upgrade_db: ##  Накатывает миграции в postgres
	uv run alembic upgrade $(up)

postgres_downgrade_db: ## Откатывает 1 миграцию назад от текущей точки
	uv run alembic downgrade $(down)

install_packages_prod: ## Устанавливает все пакеты кроме dev зависимостей
	uv sync --no-dev --frozen --no-cache

install_packages_dev: ## Устанавливает все пакеты в том числе и dev зависимостей
	uv sync --frozen

postgres_migrations_check: ## Проверка не примененных изменений в Постгресе.
	@uv run alembic check && \
	echo "Command succeeded" || \
	{ exit 1; }

print:
	@cat $(MAKEFILE_LIST) | sed 's/^/    /'  # Indent each line for better readability
