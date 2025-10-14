.PHONY: up down logs ps lint typecheck fmt build

up:
	cd infra && docker-compose up -d --build

down:
	cd infra && docker-compose down -v

logs:
	cd infra && docker-compose logs -f --tail=200

ps:
	cd infra && docker compose ps

lint:
	ruff check auth-svc task-svc notify-svc

typecheck:
	mypy auth-svc task-svc notify-svc

fmt:
	ruff format auth-svc task-svc notify-svc

build:
	cd infra && docker compose build


