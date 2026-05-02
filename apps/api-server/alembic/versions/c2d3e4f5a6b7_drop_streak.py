"""drop_streak

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-02-23 00:00:01.000000

⚠️  반드시 아래 순서로 실행할 것:
  1. alembic upgrade b1c2d3e4f5a6          (신규 테이블 생성)
  2. python scripts/migrate_streak_to_user_date_record.py  (데이터 이전)
  3. alembic upgrade c2d3e4f5a6b7          (이 파일: streak + streak_id DROP)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. problem_history → streak FK 제거: 이름을 DB에서 직접 조회해서 삭제
    conn = op.get_bind()
    fk_rows = conn.execute(sa.text("""
        SELECT CONSTRAINT_NAME
        FROM information_schema.KEY_COLUMN_USAGE
        WHERE TABLE_SCHEMA = DATABASE()
          AND TABLE_NAME = 'problem_history'
          AND REFERENCED_TABLE_NAME = 'streak'
    """)).fetchall()
    for row in fk_rows:
        try:
            op.drop_constraint(row[0], 'problem_history', type_='foreignkey')
        except Exception:
            pass

    # 2. problem_history.streak_id 컬럼 제거
    try:
        op.drop_column('problem_history', 'streak_id')
    except Exception:
        pass

    # 3. streak 테이블 제거
    try:
        op.drop_index('idx_bj_account_date', table_name='streak')
    except Exception:
        pass
    try:
        op.drop_table('streak')
    except Exception:
        pass


def downgrade() -> None:
    # streak 복원
    op.create_table(
        'streak',
        sa.Column('streak_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bj_account_id', sa.String(length=50), nullable=False),
        sa.Column('streak_date', sa.Date(), nullable=False),
        sa.Column('solved_count', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['bj_account_id'], ['bj_account.bj_account_id'], ),
        sa.PrimaryKeyConstraint('streak_id'),
    )
    op.create_index('idx_bj_account_date', 'streak', ['bj_account_id', 'streak_date'])

    # problem_history.streak_id 복원
    op.add_column('problem_history', sa.Column('streak_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'problem_history', 'streak', ['streak_id'], ['streak_id'])
