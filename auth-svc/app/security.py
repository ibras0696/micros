from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import uuid
from jose import jwt
from passlib.context import CryptContext
from app.settings import settings

pwd_ctx = CryptContext(schemes=['bcrypt'], deprecated="auto")

# Загрузка ключей (PEM)
PRIVATE_KEY = Path(settings.JWT_PRIVATE_KEY_PATH).read_text()
PUBLIC_KEY = Path(settings.JWT_PUBLIC_KEY_PATH).read_text()
ALGO = "RS256"


# Пароли
def _now() -> datetime:
    """
    Получение текущего времени в UTC
    :return: datetime: текущее время в UTC
    """
    return datetime.now(tz=timezone.utc)


def make_access_token(sub: str) -> str:
    """
    Создание access токена
    :param sub: str: subject токена (обычно user_id)
    :return: str: сгенерированный access токен
    """
    exp = _now() + timedelta(seconds=settings.ACCESS_TTL)
    payload: dict[str, Any] = {'sub': sub, 'iss': settings.JWT_ISS, 'exp': exp}
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGO)


def make_refresh_token(sub: str, jti: str) -> str:
    """
    Создание refresh токена
    :param sub: str: subject токена (обычно user_id)
    :param jti: str: уникальный идентификатор токена
    :return: str: сгенерированный refresh токен
    """
    exp = _now() + timedelta(seconds=settings.REFRESH_TTL)
    payload: dict[str, Any] = {'sub': sub, 'iss': settings.JWT_ISS, 'exp': exp, 'jti': jti}
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGO)


def verify_access(token: str) -> dict[str, Any]:
    """
    Проверка access токена
    :param token: str: access токен
    :return: dict[str, Any]: полезная нагрузка токена
    """
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGO], options={'verify_aud': False})


def verify_refresh(token: str) -> dict[str, Any]:
    """
    Проверка refresh токена
    :param token: str: refresh токен
    :return: dict[str, Any]: полезная нагрузка токена
    """
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGO], options={'verify_aud': False})


def new_jti() -> str:
    """
    Генерация нового уникального идентификатора токена (jti)
    :return: str: сгенерированный jti
    """
    return str(uuid.uuid4())
