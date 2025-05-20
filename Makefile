SHELL := /bin/bash
.PHONY: all
.DEFAULT_GOAL := help

postgres_downgrade_db: down = -1
postgres_upgrade_db: up = head
test: path =
test: args = -vv

OS := $(shell uname)

ENVIRONMENT ?= DEVELOPMENT
ENVIRONMENT := $(ENVIRONMENT)
ifeq ($(ENVIRONMENT),PRODUCTION)
    NO_CACHE_FLAG = --no-cache
else
    NO_CACHE_FLAG =
endif


help:  ## help as usual
	uvx $(NO_CACHE_FLAG) --no-progress --from rich-cli rich README.md --theme monokai --hyperlinks --pager

postgres_migration:  ## Создает файл миграции с изменениями в моделях
	uv run alembic revision --autogenerate -m "$(message)"

postgres_upgrade_db: ##  Накатывает миграции в postgres
	uv run alembic upgrade $(up)

postgres_downgrade_db: ## Откатывает 1 миграцию назад от текущей точки
	uv run alembic downgrade $(down)

install_packages_prod: ## Устанавливает все пакеты кроме dev зависимостей
	uv sync --no-dev --frozen --no-cache

install_packages_dev: ## Устанавливает все пакеты в том числе и dev зависимости
	uv sync --frozen

postgres_migrations_check: ## Проверка не примененных изменений в Постгресе
	uv run alembic check || exit $?

print: ##  Вывод содержимого Makefile в консоль
	@cat $(MAKEFILE_LIST) | sed 's/^/    /'

prefect_ui: ## UI Prefect
	xdg-open http://localhost:4200

prefect_server: ## Prefect server start
	 uv run prefect server start

test: ## Run pytest
	uv run pytest $(args) $(path)

kafka_ui_server: ## Run Kafka-ui and open default page
	@java -jar /opt/kafka-ui/kafka-ui-api-v0.7.2.jar --spring.config.location=file:/opt/kafka-ui/config/application.yml \
	& $(MAKE) kafka_ui

kafka_ui: ## WEB UI for Kafka
	xdg-open http://localhost:8080

kafka_ui_server_stop: ## Stop Kafka UI server
	@pkill -f kafka-ui

faststream: ## Run faststream
	uv run faststream run faststream_serve:app
