"""add_system_log

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-02-25 00:00:00.000000

변경 내용:
  - system_log 테이블 신규 생성
  - scheduler_log 테이블 DROP (system_log로 통합)
  - problem_update_history 테이블 DROP (system_log로 통합)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'd3e4f5a6b7c8'
down_revision: Union[str, Sequence[str], None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. system_log 테이블 생성
    op.create_table(
        'system_log',
        sa.Column('system_log_id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('log_type', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('log_data', mysql.JSON(), nullable=False),
        sa.Column('should_notify', sa.Boolean(), nullable=False, server_default=sa.text('0')),
        sa.Column('notification_data', mysql.JSON(), nullable=True),
        sa.Column('notification_sent', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('system_log_id'),
    )
    op.create_index('idx_system_log_type', 'system_log', ['log_type'], unique=False)
    op.create_index('idx_system_log_type_status', 'system_log', ['log_type', 'status'], unique=False)
    op.create_index('idx_system_log_created', 'system_log', ['created_at'], unique=False)

    # 2. scheduler_log 테이블 DROP
    # MySQL: 외래키 제약이 인덱스를 사용 중이므로 외래키를 먼저 삭제
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'scheduler_log' "
        "AND REFERENCED_TABLE_NAME IS NOT NULL"
    ))
    for row in result:
        conn.execute(sa.text(f"ALTER TABLE `scheduler_log` DROP FOREIGN KEY `{row[0]}`"))
    op.drop_table('scheduler_log', if_exists=True)

    # 3. problem_update_history 테이블 DROP
    result = conn.execute(sa.text(
        "SELECT CONSTRAINT_NAME FROM information_schema.KEY_COLUMN_USAGE "
        "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'problem_update_history' "
        "AND REFERENCED_TABLE_NAME IS NOT NULL"
    ))
    for row in result:
        conn.execute(sa.text(f"ALTER TABLE `problem_update_history` DROP FOREIGN KEY `{row[0]}`"))
    op.drop_table('problem_update_history', if_exists=True)


def downgrade() -> None:
    # 1. problem_update_history 테이블 복구
    op.create_table(
        'problem_update_history',
        sa.Column('problem_update_history_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('problem_id', sa.Integer(), nullable=False),
        sa.Column('problem_update_log', mysql.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['problem_id'], ['problem.problem_id'], ),
        sa.PrimaryKeyConstraint('problem_update_history_id'),
    )

    # 2. scheduler_log 테이블 복구
    op.create_table(
        'scheduler_log',
        sa.Column('scheduler_log_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('bj_account_id', sa.String(length=50), nullable=False),
        sa.Column('run_date', sa.Date(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('log_data', mysql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
        sa.ForeignKeyConstraint(['bj_account_id'], ['bj_account.bj_account_id'], ),
        sa.PrimaryKeyConstraint('scheduler_log_id'),
    )
    op.create_index('idx_scheduler_log', 'scheduler_log', ['bj_account_id', 'run_date'], unique=False)

    # 3. system_log 테이블 DROP
    op.drop_index('idx_system_log_created', table_name='system_log')
    op.drop_index('idx_system_log_type_status', table_name='system_log')
    op.drop_index('idx_system_log_type', table_name='system_log')
    op.drop_table('system_log')
