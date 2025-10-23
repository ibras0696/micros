# === Global Makefile for microservice project ===
.PHONY: up down logs ps lint typecheck fmt build test clean venv deps all

# === Docker orchestration ===
up: ## Запуск всех сервисов (docker compose up)
	@echo "🐳 Starting services..."
	cd infra && docker compose up -d --build

down: ## Остановка всех контейнеров и без удаления
	@echo "🛑 Stopping services..."
	cd infra && docker compose down

down_del: ## Остановка всех контейнеров и удаление volume
	@echo "🛑 Stopping services..."
	cd infra && docker compose down -v

down_up_logs: ## Перезапуск всех сервисов с просмотром логов
	@echo "🔄 Restarting services with logs..."
	cd infra && docker compose down && docker compose up -d --build && docker-compose logs -f --tail=200

logs: ## Просмотр последних логов всех контейнеров
	cd infra && docker compose logs -f --tail=200

ps: ## Список запущенных контейнеров
	cd infra && docker compose ps

build: ## Сборка всех сервисов
	@echo "🏗️  Building Docker images..."
	cd infra && docker compose build

# === Local environment ===
venv: ## Создание виртуального окружения
	@echo "🐍 Creating virtual environment..."
	python3 -m venv .venv && . .venv/bin/activate && pip -V

deps: ## Установка зависимостей (для всех сервисов)
	@echo "📦 Installing dev dependencies..."
	pip install -U pip && pip install -e "auth-svc[dev]" -e "task-svc" -e "notify-svc"

# === Quality gates ===
lint: ## Проверка стиля Ruff
	@echo "🔍 Running Ruff lint..."
	ruff check auth-svc task-svc notify-svc --fix --config tooling/ruff.toml

fmt: ## Форматирование Ruff
	@echo "🧹 Formatting code..."
	ruff format auth-svc task-svc notify-svc

typecheck: ## Статическая типизация MyPy
	@echo "🔎 Running MyPy type checking..."
	mypy auth-svc task-svc notify-svc --config-file tooling/mypy.ini

# === Testing ===
test: ## Запуск тестов для всех сервисов
	@echo "🧪 Running pytest suite..."
	pytest -v --maxfail=1 --disable-warnings --color=yes

# === Utilities ===
clean: ## Очистка кешей и временных файлов
	@echo "🧺 Cleaning Python caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache .mypy_cache .ruff_cache .coverage coverage.xml

# === Composite target ===
all: clean lint typecheck test ## Полный цикл проверки перед коммитом
	@echo "✅ All checks passed successfully!"
