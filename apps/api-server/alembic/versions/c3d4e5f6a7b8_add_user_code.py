"""add_user_code

Revision ID: c3d4e5f6a7b8
Revises: b1c2d3e4f5a6
Create Date: 2026-03-02 00:00:00.000000

변경 내용:
1. user_account 테이블에 user_code VARCHAR(6) 컬럼 추가
2. 기존 유저 backfill (랜덤 6자리, 중복 없이)
3. NOT NULL 제약 + UNIQUE 인덱스 생성
"""
import random
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text

revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _insp():
    return sa.inspect(op.get_bind())


def _column_exists(table: str, column: str) -> bool:
    return column in [c['name'] for c in _insp().get_columns(table)]


def _index_exists(table: str, index: str) -> bool:
    return any(i['name'] == index for i in _insp().get_indexes(table))


def upgrade() -> None:
    conn = op.get_bind()

    # 1. ADD COLUMN user_code VARCHAR(6) NULL (멱등성)
    if not _column_exists('user_account', 'user_code'):
        op.add_column(
            'user_account',
            sa.Column('user_code', sa.String(6), nullable=True)
        )

    # 2. 기존 유저 backfill
    result = conn.execute(
        text("SELECT user_account_id FROM user_account WHERE user_code IS NULL")
    )
    user_ids = [row[0] for row in result.fetchall()]

    used_codes: set[str] = set()
    # 이미 배정된 코드 수집
    existing = conn.execute(
        text("SELECT user_code FROM user_account WHERE user_code IS NOT NULL")
    )
    for row in existing.fetchall():
        if row[0]:
            used_codes.add(row[0])

    for uid in user_ids:
        for _ in range(100):
            code = f"{random.randint(0, 999999):06d}"
            if code not in used_codes:
                used_codes.add(code)
                conn.execute(
                    text("UPDATE user_account SET user_code = :code WHERE user_account_id = :uid"),
                    {"code": code, "uid": uid}
                )
                break

    # 3. ALTER COLUMN NOT NULL
    op.alter_column(
        'user_account', 'user_code',
        existing_type=sa.String(6),
        nullable=False,
        server_default="000000"
    )

    # 4. UNIQUE INDEX
    if not _index_exists('user_account', 'idx_user_code'):
        op.create_index('idx_user_code', 'user_account', ['user_code'], unique=True)


def downgrade() -> None:
    try:
        op.drop_index('idx_user_code', table_name='user_account')
    except Exception:
        pass
    try:
        op.drop_column('user_account', 'user_code')
    except Exception:
        pass
