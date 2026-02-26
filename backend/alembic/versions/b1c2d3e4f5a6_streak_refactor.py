"""streak_refactor

Revision ID: b1c2d3e4f5a6
Revises: a1b2c3d4e5f6
Create Date: 2026-02-23 00:00:00.000000

변경 내용:
1. user_date_record 테이블 생성 (streak 대체, 유저+BJ계정 단위)
2. scheduler_log 테이블 생성 (스케줄러 실행 이력)
3. problem_date_record: user_account_id 추가, user_problem_status_id nullable, 인덱스 추가
4. user_problem_status: bj_account_id 추가, unique constraint 변경
5. problem_history: streak_id FK 및 컬럼 제거

※ streak 테이블은 다음 마이그레이션(c2d3e4f5a6b7)에서 제거
   반드시 데이터 마이그레이션 스크립트 실행 후 적용할 것
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

from scripts.migrate_streak_to_user_date_record import run_migration

revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# ── 멱등성 헬퍼 ────────────────────────────────────────────────────────────────
# MySQL은 DDL이 트랜잭션이 아니라 부분 실패 후 재실행 시 중복 에러가 발생한다.
# 각 DDL 전에 존재 여부를 확인해 이미 적용된 작업은 건너뛴다.

def _insp():
    return sa.inspect(op.get_bind())

def _table_exists(name: str) -> bool:
    return _insp().has_table(name)

def _column_exists(table: str, column: str) -> bool:
    return column in [c['name'] for c in _insp().get_columns(table)]

def _index_exists(table: str, index: str) -> bool:
    return any(i['name'] == index for i in _insp().get_indexes(table))

def _fk_exists(table: str, fk_name: str) -> bool:
    return any(fk['name'] == fk_name for fk in _insp().get_foreign_keys(table))

def _unique_exists(table: str, constraint_name: str) -> bool:
    return any(
        uc['name'] == constraint_name
        for uc in _insp().get_unique_constraints(table)
    )


def upgrade() -> None:
    # =========================================================================
    # 1. user_date_record 테이블 생성
    # =========================================================================
    if not _table_exists('user_date_record'):
        op.create_table(
            'user_date_record',
            sa.Column('user_date_record_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('user_account_id', sa.Integer(), nullable=False),
            sa.Column('bj_account_id', sa.String(length=50), nullable=False),
            sa.Column('marked_date', sa.Date(), nullable=False),
            sa.Column('solved_count', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
            sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('NOW()')),
            sa.ForeignKeyConstraint(['user_account_id'], ['user_account.user_account_id'], ),
            sa.ForeignKeyConstraint(['bj_account_id'], ['bj_account.bj_account_id'], ),
            sa.PrimaryKeyConstraint('user_date_record_id'),
            sa.UniqueConstraint('user_account_id', 'bj_account_id', 'marked_date', name='uk_user_date'),
            comment='유저+BJ계정 단위 날짜별 풀이 수 (streak 대체)'
        )
    if not _index_exists('user_date_record', 'idx_user_date_record'):
        op.create_index('idx_user_date_record', 'user_date_record', ['user_account_id', 'bj_account_id', 'marked_date'])

    # =========================================================================
    # 2. scheduler_log 테이블 생성
    # =========================================================================
    if not _table_exists('scheduler_log'):
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
            comment='스케줄러 실행 이력'
        )
    if not _index_exists('scheduler_log', 'idx_scheduler_log'):
        op.create_index('idx_scheduler_log', 'scheduler_log', ['bj_account_id', 'run_date'])

    # =========================================================================
    # 3. problem_date_record 수정
    # =========================================================================
    if not _column_exists('problem_date_record', 'user_account_id'):
        op.add_column('problem_date_record', sa.Column('user_account_id', sa.Integer(), nullable=True))
    if not _fk_exists('problem_date_record', 'fk_pdr_user_account'):
        op.create_foreign_key(
            'fk_pdr_user_account', 'problem_date_record', 'user_account',
            ['user_account_id'], ['user_account_id']
        )
    if not _index_exists('problem_date_record', 'idx_pdr_user_account'):
        op.create_index('idx_pdr_user_account', 'problem_date_record', ['user_account_id', 'marked_date'])
    op.alter_column('problem_date_record', 'user_problem_status_id', existing_type=sa.Integer(), nullable=True)

    # =========================================================================
    # 4. user_problem_status: bj_account_id 추가, unique constraint 변경
    # =========================================================================
    if not _column_exists('user_problem_status', 'bj_account_id'):
        op.add_column('user_problem_status', sa.Column('bj_account_id', sa.String(length=50), nullable=True))
    if not _fk_exists('user_problem_status', 'fk_ups_bj_account'):
        op.create_foreign_key(
            'fk_ups_bj_account', 'user_problem_status', 'bj_account',
            ['bj_account_id'], ['bj_account_id']
        )
    # 기존 uk_user_problem(user_account_id, problem_id) 제거 후 새 unique constraint 생성
    try:
        op.drop_constraint('uk_user_problem', 'user_problem_status', type_='unique')
    except Exception:
        pass
    if not _unique_exists('user_problem_status', 'uk_user_problem'):
        op.create_unique_constraint(
            'uk_user_problem', 'user_problem_status',
            ['user_account_id', 'bj_account_id', 'problem_id']
        )
    # 기존 인덱스 재생성 (bj_account_id 포함)
    try:
        op.drop_index('idx_user_status', table_name='user_problem_status')
    except Exception:
        pass
    if not _index_exists('user_problem_status', 'idx_user_status'):
        op.create_index('idx_user_status', 'user_problem_status',
                        ['user_account_id', 'bj_account_id', 'banned_yn', 'solved_yn'])

    # =========================================================================
    # 5. problem_history.streak_id 제거는 c2d3e4f5a6b7 에서 수행
    #    (데이터 마이그레이션 스크립트가 streak_id JOIN을 사용하기 때문)
    # =========================================================================
    run_migration()

def downgrade() -> None:
    # (5는 c2d3e4f5a6b7 downgrade에서 처리)

    # 4. user_problem_status 롤백
    # try:
    #     op.drop_index('idx_user_status', table_name='user_problem_status')
    # except Exception:
    #     pass
    # try:
    #     op.drop_constraint('uk_user_problem', 'user_problem_status', type_='unique')
    # except Exception:
    #     pass
    # op.create_unique_constraint('uk_user_problem', 'user_problem_status', ['user_account_id', 'problem_id'])
    # op.create_index('idx_user_status', 'user_problem_status', ['user_account_id', 'banned_yn', 'solved_yn'])
    # try:
    #     op.drop_constraint('fk_ups_bj_account', 'user_problem_status', type_='foreignkey')
    # except Exception:
    #     pass
    # op.drop_column('user_problem_status', 'bj_account_id')

    # 3. problem_date_record 롤백
    try:
        op.drop_index('idx_pdr_user_account', table_name='problem_date_record')
    except Exception:
        pass
    try:
        op.drop_constraint('fk_pdr_user_account', 'problem_date_record', type_='foreignkey')
    except Exception:
        pass
    try:
        op.alter_column('problem_date_record', 'user_problem_status_id', existing_type=sa.Integer(), nullable=False)
    except Exception:
        pass
    try:
        op.drop_column('problem_date_record', 'user_account_id')
    except Exception:
        pass

    # 2. scheduler_log 제거
    try:
        op.drop_index('idx_scheduler_log', table_name='scheduler_log')
    except Exception:
        pass
    try:
        op.drop_table('scheduler_log')
    except Exception:
        pass

    # 1. user_date_record 제거
    try:
        op.drop_index('idx_user_date_record', table_name='user_date_record')
    except Exception:
        pass
    try:
        op.drop_table('user_date_record')
    except Exception:
        pass