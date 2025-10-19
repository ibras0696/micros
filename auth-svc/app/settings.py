from __future__ import annotations
import os

import dotenv
from pydantic import BaseModel

dotenv.load_dotenv()


class Settings(BaseModel):
    """
    Настройки приложения
    DATABASE_URL: str - URL базы данных
    JWT_PRIVATE_KEY_PATH: str - Путь к приватному ключу для JWT
    JWT_PUBLIC_KEY_PATH: str - Путь к публичному ключу для JWT
    ACCESS_TTL: int - Время жизни access токена в секундах
    REFRESH_TTL: int - Время жизни refresh токена в секундах
    JWT_ISS: str - Издатель JWT токенов
    """
    DATABASE_URL: str = os.getenv("DATABASE_URL", 'sqlite+aiosqlite:///./auth.db')

    JWT_PRIVATE_KEY_PATH: str = os.getenv('JWT_PRIVATE_KEY_PATH', './jwt_private.pem')
    JWT_PUBLIC_KEY_PATH: str = os.getenv('JWT_PUBLIC_KEY_PATH', './jwt_public.pem')
    ACCESS_TTL: int = int(os.getenv('ACCESS_TTL', '900'))
    REFRESH_TTL: int = int(os.getenv('REFRESH_TTL', '2592000'))
    JWT_ISS: str = os.getenv("JWT_ISS", "taskhub-auth")


settings = Settings()
