# syntax=docker/dockerfile:1.7

# === Base image ===
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY pyproject.toml ./

# Кэшируем зависимости
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install ".[dev]"

COPY app ./app
COPY alembic.ini ./
COPY alembic ./alembic

# === Runtime stage ===
FROM base AS runtime
COPY --from=base /usr/local /usr/local
WORKDIR /app
EXPOSE 8001

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]

# === Healthcheck ===
HEALTHCHECK CMD curl --fail http://localhost:8001/health || exit 1
