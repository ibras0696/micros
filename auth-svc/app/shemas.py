from __future__ import annotations
from pydantic import BaseModel, EmailStr


class RegisterIn(BaseModel):
    """
    Входные данные для регистрации
    """
    email: EmailStr
    password: str


class LoginIn(BaseModel):
    """
    Входные данные для логина
    """
    email: EmailStr
    password: str


class TokenPairOut(BaseModel):
    """
    Обновленная пара токенов после логина или рефреша
    """
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class MeOut(BaseModel):
    """
    Данные о пользователе
    """
    id: str
    email: EmailStr
