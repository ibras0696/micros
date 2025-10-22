.PHONY: venv deps install migrate revision test cov run clean build all

venv: # Создание и активация виртуального окружения
	python -m venv .venv && . .venv/bin/activate && pip -V

deps: # Установка зависимостей проекта
	pip install -U pip && pip install -e ".[dev]"

# Установка зависимостей и применение миграций
install: deps migrate

revision: # Создание новой миграции базы данных
	alembic revision -m "auto" --autogenerate

migrate: # Применение миграций базы данных
	alembic upgrade head

test: # Запуск тестов
	pytest -q

cov: # Запуск тестов с отчетом о покрытии
	pytest --cov=app --cov-report=term-missing

run: # Запуск приложения
	uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

clean: # Очистка временных файлов и кэша
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .coverage build dist *.egg-info

build: # Построение Docker-образа
	docker build -t auth-svc:latest .

all: clean deps test
