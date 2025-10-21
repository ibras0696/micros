# tests/conftest.py
from __future__ import annotations
import os
import asyncio
import pytest
from pathlib import Path
from httpx import AsyncClient

# === 1) Готовим окружение ДО импортов приложения ===
# shared in-memory sqlite (одна БД для всех коннектов)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///file:test.db?mode=memory&cache=shared&uri=true"
os.environ["ACCESS_TTL"] = "60"
os.environ["REFRESH_TTL"] = "3060"

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
def jwt_keys(tmp_path_factory: pytest.TempPathFactory):
    tmp = tmp_path_factory.mktemp("keys")
    priv = tmp / "jwt_private.pem"
    pub = tmp / "jwt_public.pem"

    # ⚠️ Лучше положить реальные ключи. Для примера — простые строки (HS256 проще)
    # Если используешь RS256 — подставь валидные PEM.
    priv.write_text("test-secret")  # если перейдёшь на HS256
    pub.write_text("test-public")   # для RS256 замени на реальный PUBLIC

    # Если у тебя security.py читает файлы по путям:
    os.environ["JWT_PRIVATE_KEY_PATH"] = str(priv)
    os.environ["JWT_PUBLIC_KEY_PATH"] = str(pub)

    return {"priv": priv, "pub": pub}

# === 2) Теперь можно импортировать приложение/БД ===
import app.main
from app.db import Base, engine

@pytest.fixture(scope="session", autouse=True)
async def prepare_db():
    # создаём схему один раз
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # чистим схему
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client():
    async with AsyncClient(app=app.main.app, base_url="http://testserver") as ac:
        yield ac
