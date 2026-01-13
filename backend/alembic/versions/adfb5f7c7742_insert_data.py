"""insert_data

Revision ID: adfb5f7c7742
Revises: e5b6ca7e3819
Create Date: 2026-01-02 09:48:30.604960

"""
from typing import Sequence, Union

# revision identifiers, used by Alembic.
revision: str = 'adfb5f7c7742'
down_revision: Union[str, Sequence[str], None] = 'e5b6ca7e3819'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### end Alembic commands ###
