"""add_is_synced_to_account_link

Revision ID: a1b2c3d4e5f6
Revises: 3f0a6a57a553
Create Date: 2026-02-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = '3f0a6a57a553'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('account_link', sa.Column('is_synced', sa.Boolean(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('account_link', 'is_synced')
