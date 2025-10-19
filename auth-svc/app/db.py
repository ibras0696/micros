from __future__ import annotations

from typing import Any, AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.settings import settings


class Base(DeclarativeBase):
    pass


engine: AsyncEngine = create_async_engine(settings.DATABASE_URL, echo=False, future=True)
SessionLocal = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)


async def get_session() -> AsyncGenerator[AsyncSession | Any, Any]:
    """
    Получение сессии для работы с БД
    :return: AsyncGenerator[AsyncSession | Any, Any]:
    """
    async with SessionLocal() as session:
        yield session
