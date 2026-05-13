"""github enum add

Revision ID: 41282e124456
Revises: 46664d739d74
Create Date: 2026-01-12 23:27:32.391576

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '41282e124456'
down_revision: Union[str, Sequence[str], None] = '46664d739d74'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add GITHUB to the Provider enum in MySQL
    op.execute("ALTER TABLE user_account MODIFY COLUMN provider ENUM('KAKAO', 'NAVER', 'GOOGLE', 'GITHUB', 'NONE') NOT NULL")


def downgrade() -> None:
    """Downgrade schema."""
    # Remove GITHUB from the Provider enum
    op.execute("ALTER TABLE user_account MODIFY COLUMN provider ENUM('KAKAO', 'NAVER', 'GOOGLE', 'NONE') NOT NULL")