import pytest
from httpx import AsyncClient

pytestmark = pytest.mark.anyio


async def test_register_login_me_refresh(client: AsyncClient):
    """
    Полный сценарий: регистрация, получение данных о себе, логин, рефреш с ротацией
    :param client: AsyncClient: асинхронный HTTP клиент
    :return: None
    """
    # 1) регистрация
    r = await client.post("/auth/register", json={"email": "u@example.com", "password": "secret123"})
    assert r.status_code == 201, r.text
    reg = r.json()
    assert {"access_token", "refresh_token"} <= reg.keys()

    # 2) доступ к /auth/me с access
    headers = {"Authorization": f"Bearer {reg['access_token']}"}
    me = await client.get("/auth/me", headers=headers)
    assert me.status_code == 200, me.text
    assert me.json()["email"] == "u@example.com"

    # 3) логин (получаем вторую пару токенов)
    r2 = await client.post("/auth/login", json={"email": "u@example.com", "password": "secret123"})
    assert r2.status_code == 200, r2.text
    tokens2 = r2.json()
    assert {"access_token", "refresh_token"} <= tokens2.keys()

    # 4) refresh (ротация)
    r3 = await client.post("/auth/refresh", json={"refresh_token": tokens2["refresh_token"]})
    assert r3.status_code == 200, r3.text
    tokens3 = r3.json()
    assert {"access_token", "refresh_token"} <= tokens3.keys()
    assert tokens3["refresh_token"] != tokens2["refresh_token"], "refresh должен ротироваться"

    # 5) старый refresh больше невалиден
    r4 = await client.post("/auth/refresh", json={"refresh_token": tokens2["refresh_token"]})
    assert r4.status_code == 401, r4.text
