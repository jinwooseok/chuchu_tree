"""github enum add

Revision ID: 46664d739d74
Revises: 36ad2838530f
Create Date: 2026-01-12 23:21:22.060856

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '46664d739d74'
down_revision: Union[str, Sequence[str], None] = '36ad2838530f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass

def downgrade() -> None:
    """Downgrade schema."""
    pass