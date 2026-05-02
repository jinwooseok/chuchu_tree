"""notice_remove_reference_columns

Revision ID: j1f2a3b4c5d6
Revises: i0e1f2a3b4c5
Create Date: 2026-03-11 00:00:00.000000

변경 내용:
1. notice.reference_id, notice.reference_type 컬럼 제거
   - 제거 전, reference_id 값을 content JSON에 semantic key로 이전
     - reference_type = 'STUDY_INVITATION'  → content.invitationId
     - reference_type = 'STUDY_APPLICATION' → content.applicationId
     - reference_type = 'STUDY_PROBLEM'     → content.studyProblemId
     - reference_type = 'STUDY'             → content.studyId (이미 존재하므로 스킵)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'j1f2a3b4c5d6'
down_revision: Union[str, None] = 'i0e1f2a3b4c5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. 제약조건 확인: reference_id, reference_type은 FK 없음 (nullable 컬럼)
    #    인덱스도 없으므로 바로 데이터 이전 후 DROP 가능

    # 2. reference_id → content JSON으로 이전 (이미 해당 키가 없는 경우에만)
    op.execute(
        "UPDATE notice "
        "SET content = JSON_SET(content, '$.invitationId', reference_id) "
        "WHERE reference_type = 'STUDY_INVITATION' "
        "  AND reference_id IS NOT NULL "
        "  AND JSON_EXTRACT(content, '$.invitationId') IS NULL"
    )
    op.execute(
        "UPDATE notice "
        "SET content = JSON_SET(content, '$.applicationId', reference_id) "
        "WHERE reference_type = 'STUDY_APPLICATION' "
        "  AND reference_id IS NOT NULL "
        "  AND JSON_EXTRACT(content, '$.applicationId') IS NULL"
    )
    op.execute(
        "UPDATE notice "
        "SET content = JSON_SET(content, '$.studyProblemId', reference_id) "
        "WHERE reference_type = 'STUDY_PROBLEM' "
        "  AND reference_id IS NOT NULL "
        "  AND JSON_EXTRACT(content, '$.studyProblemId') IS NULL"
    )
    # reference_type = 'STUDY': studyId는 이미 content에 존재 → 별도 이전 불필요

    # 3. 컬럼 제거
    op.drop_column('notice', 'reference_id')
    op.drop_column('notice', 'reference_type')


def downgrade() -> None:
    # 컬럼 복원 (데이터 복원은 불가 - content에서 역추출하려면 별도 스크립트 필요)
    op.add_column('notice', sa.Column('reference_id', sa.Integer(), nullable=True))
    op.add_column('notice', sa.Column('reference_type', sa.String(50), nullable=True))
