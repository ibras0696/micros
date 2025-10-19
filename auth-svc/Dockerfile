# syntax=docker/dockerfile:1.7

########### builder ###########
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Если нужны компиляторы/headers (psycopg[binary] без компиляции не требует):
# RUN apt-get update && apt-get install -y --no-install-recommends build-essential gcc && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml /app/
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --upgrade pip && pip install .

COPY app /app/app
RUN pip install --no-deps .

########### runtime ###########
FROM python:3.12-slim AS runtime

# Безопаснее не root
RUN useradd -m appuser
WORKDIR /app

# Копируем только виртуалку и код
COPY --from=builder /opt/venv /opt/venv
COPY --from=builder /app/app /app/app
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

USER appuser

EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
