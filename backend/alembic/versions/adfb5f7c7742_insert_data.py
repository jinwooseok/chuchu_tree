"""insert_data

Revision ID: adfb5f7c7742
Revises: e5b6ca7e3819
Create Date: 2026-01-02 09:48:30.604960

"""
import sys
import os
from typing import Sequence, Union
from pathlib import Path

from alembic import op
import sqlalchemy as sa

# 프로젝트 루트를 sys.path에 추가
BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from db_initializer import DBMigrator, get_db_url

# revision identifiers, used by Alembic.
revision: str = 'adfb5f7c7742'
down_revision: Union[str, Sequence[str], None] = 'e5b6ca7e3819'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    DB_URL = get_db_url()
    engine = sa.create_engine(DB_URL)
    migrator = DBMigrator(engine)
    migrator.execute_init()
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    DB_URL = get_db_url()
    engine = sa.create_engine(DB_URL)
    migrator = DBMigrator(engine)
    migrator.truncate_all_tables()
    # ### end Alembic commands ###
