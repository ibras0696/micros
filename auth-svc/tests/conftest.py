# tests/conftest.py
from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from pathlib import Path
from typing import Any

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from httpx import ASGITransport, AsyncClient

# === 1) Готовим окружение ДО импортов приложения ===
os.environ["JWT_ISS"] = "taskhub-auth"
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
    Создаёт временные RSA-ключи для JWT и прописывает пути в окружении.
    :param tmp_path_factory: pytest.TempPathFactory — фабрика временных путей
    :return: dict[str, Path] — пути к приватному и публичному ключам
    """

    # Временная директория для ключей
    tmp = tmp_path_factory.mktemp("keys")
    priv = tmp / "jwt_private.pem"
    pub = tmp / "jwt_public.pem"

    # Генерируем RSA-пару (2048 бит)
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

    # Сериализуем приватный ключ (PKCS8, без пароля)
    priv_pem = key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    # Сериализуем публичный ключ (SubjectPublicKeyInfo)
    pub_pem = key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    # Сохраняем ключи во временные файлы
    priv.write_bytes(priv_pem)
    pub.write_bytes(pub_pem)

    # Прописываем пути в окружение (чтобы Settings мог их подхватить)
    os.environ["JWT_PRIVATE_KEY_PATH"] = str(priv)
    os.environ["JWT_PUBLIC_KEY_PATH"] = str(pub)

    return {"priv": priv, "pub": pub}


# === 2) Теперь можно импортировать приложение/БД ===
import app.main
from app.db import Base, engine


@pytest.fixture
def anyio_backend():
    """
    Фикстура для выбора бэкенда anyio.
    :return: str: название бэкенда
    """
    return "asyncio"


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
