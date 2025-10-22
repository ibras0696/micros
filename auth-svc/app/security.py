from __future__ import annotations
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any
import uuid
from jose import jwt
from passlib.context import CryptContext
from app.settings import settings

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Загрузка ключей (PEM)
PRIVATE_KEY = Path(settings.JWT_PRIVATE_KEY_PATH).read_text()
PUBLIC_KEY = Path(settings.JWT_PUBLIC_KEY_PATH).read_text()
ALGO = "RS256"


# Пароли

def hash_password(plain: str) -> str:
    """
    Хеширование пароля
    :param plain: простой пароль
    :return: str: захешированный пароль
    """
    return pwd_ctx.hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    """
    Проверка пароля
    :param plain: простой пароль
    :param hashed: захешированный пароль
    :return: bool: результат проверки
    """
    return pwd_ctx.verify(plain, hashed)


# JWT Access/Refresh

def _now() -> datetime:
    """
    Получение текущего времени в UTC
    :return: datetime: текущее время в UTC
    """
    return datetime.now(tz=timezone.utc)


def make_access_token(sub: str) -> str:
    """
    Создание access токена
    :param sub: объект токена (обычно user id)
    :return: str: JWT access токен
    """
    exp = _now() + timedelta(seconds=settings.ACCESS_TTL)
    payload: dict[str, Any] = {"sub": sub, "iss": settings.JWT_ISS, "exp": exp}
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGO)


def make_refresh_token(sub: str, jti: str) -> str:
    """
    Создание refresh токена
    :param sub: объект токена (обычно user id)
    :param jti: уникальный идентификатор токена
    :return: str: JWT refresh токен
    """
    exp = _now() + timedelta(seconds=settings.REFRESH_TTL)
    payload: dict[str, Any] = {"sub": sub, "iss": settings.JWT_ISS, "exp": exp, "jti": jti}
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGO)


def verify_access(token: str) -> dict[str, Any]:
    """
    Верификация access токена
    :param token: str: JWT access токен
    :return: dict[str, Any]: полезная нагрузка токена
    """
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGO], options={"verify_aud": False})


def verify_refresh(token: str) -> dict[str, Any]:
    """
    Верификация refresh токена
    :param token: str: JWT refresh токен
    :return: dict[str, Any]: полезная нагрузка токена
    """
    return jwt.decode(token, PUBLIC_KEY, algorithms=[ALGO], options={"verify_aud": False})


def new_jti() -> str:
    """
    Генерация нового уникального идентификатора JTI для refresh токена
    :return: str: новый JTI
    """
    return str(uuid.uuid4())
