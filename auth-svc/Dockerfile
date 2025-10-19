# syntax=docker/dockerfile:1.7
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

COPY pyproject.toml /app/
COPY app /app/app

RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && \
    pip install .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
