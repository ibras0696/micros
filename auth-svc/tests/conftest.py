# tests/conftest.py
from __future__ import annotations
import os
import asyncio
from asyncio import AbstractEventLoop
from typing import Any, Generator, AsyncGenerator

import pytest
from pathlib import Path
from httpx import AsyncClient, ASGITransport

# === 1) Готовим окружение ДО импортов приложения ===
# shared in-memory sqlite (одна БД для всех коннектов)
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///file:test.db?mode=memory&cache=shared&uri=true"
os.environ["ACCESS_TTL"] = "60"
os.environ["REFRESH_TTL"] = "3060"


# @pytest.fixture(scope="session")
# def event_loop() -> Generator[AbstractEventLoop, Any, None]:
#     """
#     Создаёт и закрывает событийный цикл для асинхронных тестов.
#     :return: Generator[AbstractEventLoop, Any, None]: событийный цикл
#     """
#     loop = asyncio.new_event_loop()
#     yield loop
#     loop.close()


@pytest.fixture(scope="session", autouse=True)
def jwt_keys(tmp_path_factory: pytest.TempPathFactory) -> dict[str, Path]:
    """
    Создаём временные JWT ключи и настраиваем пути в окружении.
    :param tmp_path_factory: pytest.TempPathFactory: фабрика временных путей
    :return: dict[str, Path]: пути к приватному и публичному ключам
    """
    tmp = tmp_path_factory.mktemp("keys")
    priv = tmp / "jwt_private.pem"
    pub = tmp / "jwt_public.pem"

    # ⚠️ Лучше положить реальные ключи. Для примера — простые строки (HS256 проще)
    # Если используешь RS256 — подставь валидные PEM.
    priv.write_text("test-secret")  # если перейдёшь на HS256
    pub.write_text("test-public")  # для RS256 замени на реальный PUBLIC

    # Если у тебя security.py читает файлы по путям:
    os.environ["JWT_PRIVATE_KEY_PATH"] = str(priv)
    os.environ["JWT_PUBLIC_KEY_PATH"] = str(pub)

    return {"priv": priv, "pub": pub}


# === 2) Теперь можно импортировать приложение/БД ===
import app.main
from app.db import Base, engine


@pytest.fixture(scope="function", autouse=True)
async def prepare_db() -> AsyncGenerator[None, Any]:
    """
    Создаёт и чистит схему БД перед и после сессии тестов.
    :return: None
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    try:
        yield
    finally:
        # подчистить схему и освободить коннекты всегда
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, Any]:
    """
    Фикстура для асинхронного HTTP клиента, связанного с приложением.
    :return: AsyncGenerator[AsyncClient, Any]: асинхронный HTTP клиент
    """
    transport = ASGITransport(app=app.main.app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
