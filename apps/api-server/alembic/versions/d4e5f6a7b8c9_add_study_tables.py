"""add_study_tables

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-02 01:00:00.000000

변경 내용:
1. study 테이블 생성
2. study_member 테이블 생성
3. study_invitation 테이블 생성
4. study_application 테이블 생성
5. study_problem 테이블 생성
6. notice 테이블 생성
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

revision: str = 'd4e5f6a7b8c9'
down_revision: Union[str, Sequence[str], None] = 'c3d4e5f6a7b8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _insp():
    return sa.inspect(op.get_bind())


def _table_exists(name: str) -> bool:
    return _insp().has_table(name)


def _index_exists(table: str, index: str) -> bool:
    return any(i['name'] == index for i in _insp().get_indexes(table))


def upgrade() -> None:
    # =========================================================================
    # 1. study 테이블
    # =========================================================================
    if not _table_exists('study'):
        op.create_table(
            'study',
            sa.Column('study_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('study_name', sa.String(50), nullable=False),
            sa.Column('owner_user_account_id', sa.Integer(), nullable=False),
            sa.Column('description', sa.String(200), nullable=True),
            sa.Column('max_members', sa.Integer(), nullable=False, server_default='10'),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['owner_user_account_id'], ['user_account.user_account_id']),
            sa.PrimaryKeyConstraint('study_id'),
            sa.UniqueConstraint('study_name', name='uk_study_name'),
            comment='스터디'
        )
    if not _index_exists('study', 'idx_study_owner'):
        op.create_index('idx_study_owner', 'study', ['owner_user_account_id'])

    # =========================================================================
    # 2. study_member 테이블
    # =========================================================================
    if not _table_exists('study_member'):
        op.create_table(
            'study_member',
            sa.Column('study_member_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('study_id', sa.Integer(), nullable=False),
            sa.Column('user_account_id', sa.Integer(), nullable=False),
            sa.Column('role', sa.Enum('OWNER', 'MEMBER', name='studymemberrole'), nullable=False),
            sa.Column('joined_at', sa.DateTime(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['study_id'], ['study.study_id']),
            sa.ForeignKeyConstraint(['user_account_id'], ['user_account.user_account_id']),
            sa.PrimaryKeyConstraint('study_member_id'),
            sa.UniqueConstraint('study_id', 'user_account_id', name='uk_study_member'),
            comment='스터디 멤버'
        )
    if not _index_exists('study_member', 'idx_study_member_user'):
        op.create_index('idx_study_member_user', 'study_member', ['user_account_id'])

    # =========================================================================
    # 3. study_invitation 테이블
    # =========================================================================
    if not _table_exists('study_invitation'):
        op.create_table(
            'study_invitation',
            sa.Column('invitation_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('study_id', sa.Integer(), nullable=False),
            sa.Column('invitee_user_account_id', sa.Integer(), nullable=False),
            sa.Column('inviter_user_account_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', name='invitationstatus'), nullable=False),
            sa.Column('responded_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['study_id'], ['study.study_id']),
            sa.ForeignKeyConstraint(['invitee_user_account_id'], ['user_account.user_account_id']),
            sa.ForeignKeyConstraint(['inviter_user_account_id'], ['user_account.user_account_id']),
            sa.PrimaryKeyConstraint('invitation_id'),
            sa.UniqueConstraint('study_id', 'invitee_user_account_id', name='uk_study_invitation'),
            comment='스터디 초대'
        )
    if not _index_exists('study_invitation', 'idx_study_invitation_invitee'):
        op.create_index('idx_study_invitation_invitee', 'study_invitation', ['invitee_user_account_id'])

    # =========================================================================
    # 4. study_application 테이블
    # =========================================================================
    if not _table_exists('study_application'):
        op.create_table(
            'study_application',
            sa.Column('application_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('study_id', sa.Integer(), nullable=False),
            sa.Column('applicant_user_account_id', sa.Integer(), nullable=False),
            sa.Column('status', sa.Enum('PENDING', 'ACCEPTED', 'REJECTED', name='applicationstatus'), nullable=False),
            sa.Column('message', sa.String(300), nullable=True),
            sa.Column('responded_at', sa.DateTime(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['study_id'], ['study.study_id']),
            sa.ForeignKeyConstraint(['applicant_user_account_id'], ['user_account.user_account_id']),
            sa.PrimaryKeyConstraint('application_id'),
            comment='스터디 가입신청'
        )
    if not _index_exists('study_application', 'idx_study_application_study'):
        op.create_index('idx_study_application_study', 'study_application', ['study_id', 'status'])
    if not _index_exists('study_application', 'idx_study_application_applicant'):
        op.create_index('idx_study_application_applicant', 'study_application', ['applicant_user_account_id'])

    # =========================================================================
    # 5. study_problem 테이블
    # =========================================================================
    if not _table_exists('study_problem'):
        op.create_table(
            'study_problem',
            sa.Column('study_problem_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('study_id', sa.Integer(), nullable=False),
            sa.Column('problem_id', sa.Integer(), nullable=False),
            sa.Column('target_user_account_ids', mysql.JSON(), nullable=False),
            sa.Column('assigned_by_user_account_id', sa.Integer(), nullable=False),
            sa.Column('target_date', sa.Date(), nullable=False),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['study_id'], ['study.study_id']),
            sa.ForeignKeyConstraint(['problem_id'], ['problem.problem_id']),
            sa.ForeignKeyConstraint(['assigned_by_user_account_id'], ['user_account.user_account_id']),
            sa.PrimaryKeyConstraint('study_problem_id'),
            comment='스터디 풀문제'
        )
    if not _index_exists('study_problem', 'idx_study_problem_study_date'):
        op.create_index('idx_study_problem_study_date', 'study_problem', ['study_id', 'target_date'])

    # =========================================================================
    # 6. notice 테이블
    # =========================================================================
    if not _table_exists('notice'):
        op.create_table(
            'notice',
            sa.Column('notice_id', sa.Integer(), autoincrement=True, nullable=False),
            sa.Column('recipient_user_account_id', sa.Integer(), nullable=False),
            sa.Column('category', sa.Enum(
                'STUDY_INVITATION_STATUS',
                'STUDY_APPLICATION_STATUS',
                'STUDY_PROBLEMS_STATUS',
                'USER_PROBLEMS_STATUS',
                'USER_TIER_STATUS',
                'SYSTEM_ANNOUNCEMENT',
                name='noticecategory'
            ), nullable=False),
            sa.Column('title', sa.String(200), nullable=False),
            sa.Column('content', sa.String(1000), nullable=False),
            sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'),
            sa.Column('reference_id', sa.Integer(), nullable=True),
            sa.Column('reference_type', sa.String(50), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=False),
            sa.Column('updated_at', sa.DateTime(), nullable=False),
            sa.Column('deleted_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['recipient_user_account_id'], ['user_account.user_account_id']),
            sa.PrimaryKeyConstraint('notice_id'),
            comment='알림'
        )
    if not _index_exists('notice', 'idx_notice_recipient'):
        op.create_index('idx_notice_recipient', 'notice',
                        ['recipient_user_account_id', 'is_read', 'created_at'])


def downgrade() -> None:
    # 역순으로 제거
    try:
        op.drop_index('idx_notice_recipient', table_name='notice')
    except Exception:
        pass
    try:
        op.drop_table('notice')
    except Exception:
        pass

    try:
        op.drop_index('idx_study_problem_study_date', table_name='study_problem')
    except Exception:
        pass
    try:
        op.drop_table('study_problem')
    except Exception:
        pass

    try:
        op.drop_index('idx_study_application_applicant', table_name='study_application')
    except Exception:
        pass
    try:
        op.drop_index('idx_study_application_study', table_name='study_application')
    except Exception:
        pass
    try:
        op.drop_table('study_application')
    except Exception:
        pass

    try:
        op.drop_index('idx_study_invitation_invitee', table_name='study_invitation')
    except Exception:
        pass
    try:
        op.drop_table('study_invitation')
    except Exception:
        pass

    try:
        op.drop_index('idx_study_member_user', table_name='study_member')
    except Exception:
        pass
    try:
        op.drop_table('study_member')
    except Exception:
        pass

    try:
        op.drop_index('idx_study_owner', table_name='study')
    except Exception:
        pass
    try:
        op.drop_table('study')
    except Exception:
        pass

    # Enum 타입 제거 (PostgreSQL에서만 필요, MySQL은 자동 제거됨)
    try:
        op.execute('DROP TYPE IF EXISTS studymemberrole')
        op.execute('DROP TYPE IF EXISTS invitationstatus')
        op.execute('DROP TYPE IF EXISTS applicationstatus')
        op.execute('DROP TYPE IF EXISTS noticecategory')
    except Exception:
        pass
