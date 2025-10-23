from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.deps import get_current_user
from app.models import RefreshToken, User
from app.schemes import LoginIn, MeOut, RegisterIn, TokenPairOut
from app.security import (
    hash_password,
    make_access_token,
    make_refresh_token,
    new_jti,
    verify_password,
)
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
        raise HTTPException(status_code=400, detail="email already registered") from None

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
        raise HTTPException(status_code=401, detail="invalid credentials") from None

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


@router.post("/refresh", response_model=TokenPairOut)
async def refresh_token(
    data: dict,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> TokenPairOut:
    """
    Ротация refresh-токена.
    Проверяет валидность старого refresh, отзывает его и выдаёт новую пару токенов.
    :param data: тело запроса, содержащее refresh_token
    :param session: сессия базы данных
    :return: новая пара access/refresh токенов
    """
    from app.security import verify_refresh

    raw_token = data.get("refresh_token")
    if not raw_token:
        raise HTTPException(status_code=400, detail="refresh_token required") from None

    # Декодируем refresh-токен
    try:
        payload = verify_refresh(raw_token)
    except Exception:
        raise HTTPException(status_code=401, detail="invalid token") from None

    if payload.get("type") != "refresh" or not payload.get("jti"):
        raise HTTPException(status_code=401, detail="invalid token") from None

    jti_old = payload["jti"]
    user_id = payload["sub"]

    # Проверяем, что refresh существует и не отозван
    rt = (
        await session.execute(
            select(RefreshToken).where(RefreshToken.jti == jti_old, RefreshToken.user_id == user_id)
        )
    ).scalar_one_or_none()

    if not rt or rt.revoked:
        raise HTTPException(status_code=401, detail="refresh token revoked or not found")

    # Отзываем старый refresh-токен
    await session.execute(
        update(RefreshToken).where(RefreshToken.jti == jti_old).values(revoked=True)
    )

    # Создаём новый refresh-токен
    jti_new = new_jti()
    new_rt = RefreshToken(
        jti=jti_new,
        user_id=user_id,
        issued_at=utcnow(),
        expires_at=utcnow() + timedelta(seconds=settings.REFRESH_TTL),
        revoked=False,
    )
    session.add(new_rt)
    await session.commit()

    # Возвращаем новую пару токенов
    return TokenPairOut(
        access_token=make_access_token(user_id),
        refresh_token=make_refresh_token(user_id, jti_new),
    )


@router.get("/me", response_model=MeOut)
async def me(user: Annotated[User, Depends(get_current_user)]) -> MeOut:
    """
    Получение информации о текущем пользователе
    :param user: текущий пользователь
    :return: информация о пользователе
    """
    return MeOut(id=user.id, email=user.email)
