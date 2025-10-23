# === Auth Service Makefile ===
.PHONY: venv deps install migrate revision test cov lint fmt typecheck run clean build reset-db all

# ---- Python environment ----
venv: ## Создание и активация виртуального окружения
	@echo "🐍 Creating virtual environment..."
	python3 -m venv .venv && . .venv/bin/activate && pip -V

deps: ## Установка зависимостей проекта
	@echo "📦 Installing dependencies..."
	pip install -U pip && pip install -e ".[dev]" || pip install -r requirements.txt

install: deps migrate ## Установка зависимостей и применение миграций

# ---- Database & migrations ----
revision: ## Создание новой миграции
	@echo "🧱 Generating Alembic revision..."
	alembic revision -m "auto" --autogenerate

migrate: ## Применение миграций
	@echo "🚀 Applying migrations..."
	alembic upgrade head

reset-db: ## Полный сброс базы данных (только для dev)
	@echo "⚠️  Resetting local database..."
	rm -f auth.db
	alembic upgrade head

# ---- Quality gates ----
lint: ## Проверка стиля Ruff
	@echo "🔍 Running Ruff lint..."
	ruff check app tests --fix --config ../tooling/ruff.toml

fmt: ## Форматирование Ruff
	@echo "🧹 Formatting code..."
	ruff format app tests

typecheck: ## Статическая типизация MyPy
	@echo "🔎 Running MyPy..."
	mypy app tests --config-file ../tooling/mypy.ini

# ---- Tests ----
test: ## Запуск тестов
	@echo "🧪 Running tests..."
	pytest -q

cov: ## Отчет о покрытии
	@echo "📊 Running coverage..."
	pytest --cov=app --cov-report=term-missing -q

# ---- Run & build ----
run: ## Запуск приложения (локально)
	@echo "🚀 Starting FastAPI app..."
	uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload

build: ## Сборка Docker-образа
	@echo "🐳 Building Docker image..."
	docker build -t auth-svc:latest .

docker-run: build ## Запуск Docker контейнера
	@echo "🐳 Running Docker container..."
	docker run -it --rm -p 8001:8001 --name auth-svc auth-svc:latest

# ---- Maintenance ----
clean: ## Очистка кэшей и сборочных артефактов
	@echo "🧺 Cleaning caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .coverage coverage.xml build dist *.egg-info auth.db

# ---- Default target ----
all: clean deps lint typecheck test ## Полный цикл проверки
	@echo "✅ All checks passed!"
