"""per_tag_tag_skill_schema

Revision ID: a4c2e8f9d1b3
Revises: 31a0fd8f1cd1
Create Date: 2026-01-13 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a4c2e8f9d1b3'
down_revision: Union[str, Sequence[str], None] = '31a0fd8f1cd1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema for per-tag tag_skill records.

    Prerequisites:
    - db_initializer.py should have been run first to:
      1. Delete old global tag_skill records (WHERE tag_id IS NULL)
      2. Create new per-tag tag_skill records (WITH tag_id populated)
    """

    # Step 1: Drop old UNIQUE constraint (tag_level, tag_skill_code)
    op.drop_constraint('uk_tag_skill', 'tag_skill', type_='unique')

    # Step 2: Make tag_id NOT NULL
    # This will fail if any records have tag_id=NULL, so db_initializer.py must run first
    op.alter_column('tag_skill', 'tag_id',
                    existing_type=sa.Integer(),
                    nullable=False)

    # Step 3: Create new UNIQUE constraint (tag_id, tag_skill_code)
    op.create_unique_constraint('uk_tag_skill_per_tag', 'tag_skill',
                               ['tag_id', 'tag_skill_code'])


def downgrade() -> None:
    """Downgrade schema back to global tag_skill."""

    # Step 1: Drop new constraint
    op.drop_constraint('uk_tag_skill_per_tag', 'tag_skill', type_='unique')

    # Step 2: Make tag_id nullable again
    op.alter_column('tag_skill', 'tag_id',
                    existing_type=sa.Integer(),
                    nullable=True)

    # Step 3: Recreate old constraint
    op.create_unique_constraint('uk_tag_skill', 'tag_skill',
                               ['tag_level', 'tag_skill_code'])
