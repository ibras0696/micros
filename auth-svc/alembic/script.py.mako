"""${message}

Revision ID: ${up_revision}
Revises: ${down_revision | comma,n}
Create Date: ${create_date}
"""

from __future__ import annotations

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
# from sqlalchemy.dialects import postgresql as psql  # <- раскомментируй при нужде

# revision identifiers, used by Alembic.
revision: str = "${up_revision}"
down_revision: Union[str, None] = ${down_revision | repr}
branch_labels: Union[str, tuple[str, ...], None] = ${branch_labels | repr}
depends_on: Union[str, Sequence[str], None] = ${depends_on | repr}


def upgrade() -> None:
    """Apply forward migration."""
    # Автогенерация подставит сюда операции (CREATE TABLE/ADD COLUMN/...).
    # Для ручных операций — примеры:
    # op.create_table(
    #     "users",
    #     sa.Column("id", sa.Integer, primary_key=True),
    #     sa.Column("email", sa.String(254), nullable=False, unique=True, index=True),
    # )


def downgrade() -> None:
    """Revert migration."""
    # Автогенерация подставит обратные операции.
    # Для ручных операций — примеры:
    # op.drop_table("users")
