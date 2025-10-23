from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base


def utcnow() -> datetime:
    """
    Получение текущего времени в UTC
    :return: datetime: текущее время в UTC
    """
    return datetime.now(tz=timezone.utc)


class User(Base):
    """
    Модель пользователя
    """
    __tablename__ = 'users'

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow(), nullable=False)

    tokens: Mapped[list[RefreshToken]] = relationship(back_populates='user', cascade="all, delete-orphan")


class RefreshToken(Base):
    """
    Модель рефреш токена
    """
    __tablename__ = 'refresh_tokens'

    jti: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey('users.id', ondelete="CASCADE"), index=True)
    issued_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    revoked: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    replaced_by: Mapped[str | None] = mapped_column(String(36), nullable=True)

    user: Mapped[User] = relationship(back_populates='tokens')
