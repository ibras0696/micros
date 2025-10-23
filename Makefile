.PHONY: up down logs ps lint typecheck fmt build test clean

# === Docker orchestration ===
up:
	cd infra && docker compose up -d --build

down:
	cd infra && docker compose down -v

logs:
	cd infra && docker compose logs -f --tail=200

ps:
	cd infra && docker compose ps

build:
	cd infra && docker compose build

# === Quality gates ===
lint:
	@echo "🔍 Running Ruff lint..."
	ruff check auth-svc task-svc notify-svc --fix --config tooling/ruff.toml

fmt:
	@echo "🧹 Formatting code..."
	ruff format auth-svc task-svc notify-svc

typecheck:
	@echo "🔎 Running MyPy type checking..."
	mypy auth-svc task-svc notify-svc

test:
	@echo "🧪 Running pytest suite..."
	pytest -v --maxfail=1 --disable-warnings -q auth-svc/tests

# === Utilities ===
clean:
	@echo "🧺 Cleaning Python caches..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
