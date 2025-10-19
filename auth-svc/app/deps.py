from __future__ import annotations
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_session
from app.models import User
from app.security import verify_access

bearer = HTTPBearer(auto_error=True)


async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer),
    session: AsyncSession = Depends(get_session)
) -> User:
    try:
        payload = verify_access(creds.credentials)
        sub = payload.get('sub')

    except Exception:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token')

    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='invalid token')

    user = (await session.execute(select(User).where(User.id))).scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='user not found')

    return user
