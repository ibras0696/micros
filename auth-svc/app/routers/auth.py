from __future__ import annotations
from datetime import timedelta, datetime, timezone
from uuid import uuid4
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.db import get_session
from app.models import User, RefreshToken
from app.schemes import RegisterIn, LoginIn, TokenPairOut, MeOut
from app.security import hash_password, verify_password, make_access_token, make_refresh_token, new_jti
from app.deps import get_current_user
from app.settings import settings


def utcnow() -> datetime:
    """
    Получение текущего времени в UTC
    :return: datetime: текущее время в UTC
    """
    return datetime.now(tz=timezone.utc)


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register(data: RegisterIn, session: Annotated[AsyncSession, Depends(get_session)]) -> TokenPairOut:
    """
    Регистрация пользователя
    :param data: Данные для регистрации
    :param session: сессия базы данных
    :return: Пара токенов
    """
    # Проверяем уникальность email
    exists = (await session.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    if exists:
        raise HTTPException(status_code=400, detail="email already registered")

    user = User(id=str(uuid4()), email=data.email, password_hash=hash_password(data.password))
    session.add(user)
    await session.commit()

    # Создаем токер рефреш + выдать пару токенов
    jti = new_jti()
    rt = RefreshToken(
        jti=jti,
        user_id=user.id,
        issued_at=utcnow(),
        expires_at=utcnow() + timedelta(seconds=settings.REFRESH_TTL),
        revoked=False
    )
    session.add(rt)
    await session.commit()

    return TokenPairOut(
        access_token=make_access_token(user.id),
        refresh_token=make_refresh_token(user.id, jti)
    )


@router.post("/login")
async def login(data: LoginIn, session: Annotated[AsyncSession, Depends(get_session)]) -> TokenPairOut:
    """
    Логин пользователя
    :param data: Данные для логина
    :param session: сессия базы данных
    :return: Пара токенов
    """
    user = (await session.execute(select(User).where(User.email == data.email))).scalar_one_or_none()
    # Проверяем, что пользователь существует
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="invalid credentials")

    # Создаем токер рефреш + выдать пару токенов
    jti = new_jti()
    rt = RefreshToken(
        jti=jti,
        user_id=user.id,
        issued_at=utcnow(),
        expires_at=utcnow() + timedelta(seconds=settings.REFRESH_TTL),
        revoked=False
    )
    session.add(rt)
    await session.commit()

    return TokenPairOut(
        access_token=make_access_token(user.id),
        refresh_token=make_refresh_token(user.id, jti)
    )


@router.get("/me", response_model=MeOut)
async def me(user: Annotated[User, Depends(get_current_user)]) -> MeOut:
    """
    Получение информации о текущем пользователе
    :param user: текущий пользователь
    :return: информация о пользователе
    """
    return MeOut(id=user.id, email=user.email)
