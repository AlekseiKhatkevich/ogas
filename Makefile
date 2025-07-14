SHELL := /bin/bash
.PHONY: all
.DEFAULT_GOAL := help

postgres_downgrade_db: down = -1
postgres_upgrade_db: up = head
test: path =
test: args = -vv
faststream: reload =
faststream: workers = 1

OS := $(shell uname)
CPU_CORES := $(shell nproc)

ENVIRONMENT ?= DEVELOPMENT
ENVIRONMENT := $(ENVIRONMENT)

FASTSTREAM_NUM_WORKERS ?= $(CPU_CORES)  # default
FASTSTREAM_NUM_WORKERS := $(FASTSTREAM_NUM_WORKERS)

ifeq ($(ENVIRONMENT),PRODUCTION)
    NO_CACHE_FLAG = --no-cache
    faststream: workers = $(FASTSTREAM_NUM_WORKERS)
    test: args = $(args) -n auto
else
    NO_CACHE_FLAG =
    faststream: reload = --reload
    faststream: workers = 1  # always 1 for development
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
	uv run pytest $(args) --exitfirst $(path)

kafka_ui_server: ## Run Kafka-ui and open default page
	@java -jar /opt/kafka-ui/kafka-ui-api-v0.7.2.jar --spring.config.location=file:/opt/kafka-ui/config/application.yml \
	> /dev/null & $(MAKE) kafka_ui

kafka_ui: ## WEB UI for Kafka
	xdg-open http://localhost:8080

kafka_ui_server_stop: ## Stop Kafka UI server
	@pkill -f kafka-ui

faststream: ## Run faststream
	uv run faststream run faststream_serve:app $(reload) --workers $(workers)

prometheus_metrics_endpoint: ## Prometheus metric`s endpoint
	xdg-open http://localhost:8000/metrics

prometheus_ui: ## Prometheus UI browser
	xdg-open http://localhost:9090/

raven_ui: ## RavenDB user interface
	xdg-open http://127.0.0.1:8081/studio/index.html



