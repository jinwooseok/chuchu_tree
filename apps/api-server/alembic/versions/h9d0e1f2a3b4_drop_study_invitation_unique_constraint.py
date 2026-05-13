"""drop_study_invitation_unique_constraint

Revision ID: h9d0e1f2a3b4
Revises: g8c9d0e1f2a3
Create Date: 2026-03-08 00:00:00.000000

변경 내용:
1. study_invitation 테이블의 uk_study_invitation (study_id, invitee_user_account_id) unique constraint 제거
   - 취소(soft delete) 후 재초대 시 새 row INSERT 가능하도록
   - 활성 초대 중복 방지는 application 레이어에서 (status==PENDING AND deleted_at IS NULL) 조건으로 보장
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'h9d0e1f2a3b4'
down_revision: Union[str, None] = 'g8c9d0e1f2a3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # FK가 uk_study_invitation 인덱스에 의존하므로, 대체 인덱스를 먼저 생성 후 제거
    op.create_index('idx_study_invitation_study', 'study_invitation', ['study_id', 'status'])
    op.drop_constraint('uk_study_invitation', 'study_invitation', type_='unique')


def downgrade() -> None:
    op.create_unique_constraint(
        'uk_study_invitation',
        'study_invitation',
        ['study_id', 'invitee_user_account_id']
    )
    op.drop_index('idx_study_invitation_study', 'study_invitation')
