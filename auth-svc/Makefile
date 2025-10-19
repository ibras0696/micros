.PHONY: venv deps migrate revision test cov

venv:
	python -m venv .venv && . .venv/bin/activate && pip -V

deps:
	pip install -U pip && pip install .[dev]


revision:
	alembic revision -m "auto" --autogenerate


migrate:
	alembic upgrade head


test:
	pytest -q

cov:
	pytest -q --cov=app --cov-report=term-missing
