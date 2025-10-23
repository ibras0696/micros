from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import User
from app.security import verify_access

bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    session: AsyncSession = Depends(get_session)
) -> User:
    """
    Достаём пользователя из access-токена (sub = строковый UUID пользователя).
    """
    try:
        payload = verify_access(creds.credentials)
    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token') from None

    # Проверяем тип токена и наличие sub
    if payload.get('type') != 'access' or not payload.get('sub'):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token') from None

    sub: str = payload['sub']  # строковый UUID
    user = (await session.execute(select(User).where(User.id == sub))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user not found') from None

    return user
