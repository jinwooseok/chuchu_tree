"""notice_category_refactor

Revision ID: i0e1f2a3b4c5
Revises: h9d0e1f2a3b4
Create Date: 2026-03-10 00:00:00.000000

변경 내용:
1. notice.category enum 값 리네임
   - STUDY_INVITATION_STATUS → STUDY_INVITATION
   - STUDY_APPLICATION_STATUS → STUDY_APPLICATION
   - STUDY_PROBLEMS_STATUS → STUDY_PROBLEM
   - USER_PROBLEMS_STATUS → USER_PROBLEM
   - USER_TIER_STATUS → USER_TIER
2. notice.category_detail 컬럼 추가 (VARCHAR 50, nullable)
3. notice.title 컬럼 제거
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'i0e1f2a3b4c5'
down_revision: Union[str, None] = 'h9d0e1f2a3b4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. enum을 구+신 값 모두 포함하도록 확장 (UPDATE 전에 먼저)
    op.execute(
        "ALTER TABLE notice MODIFY COLUMN category ENUM("
        "'STUDY_INVITATION_STATUS', 'STUDY_APPLICATION_STATUS', 'STUDY_PROBLEMS_STATUS',"
        "'USER_PROBLEMS_STATUS', 'USER_TIER_STATUS', 'SYSTEM_ANNOUNCEMENT',"
        "'STUDY_INVITATION', 'STUDY_APPLICATION', 'STUDY_PROBLEM',"
        "'USER_PROBLEM', 'USER_TIER'"
        ") NOT NULL"
    )

    # 2. 기존 데이터를 새 값으로 업데이트
    op.execute("UPDATE notice SET category = 'STUDY_INVITATION' WHERE category = 'STUDY_INVITATION_STATUS'")
    op.execute("UPDATE notice SET category = 'STUDY_APPLICATION' WHERE category = 'STUDY_APPLICATION_STATUS'")
    op.execute("UPDATE notice SET category = 'STUDY_PROBLEM' WHERE category = 'STUDY_PROBLEMS_STATUS'")
    op.execute("UPDATE notice SET category = 'USER_PROBLEM' WHERE category = 'USER_PROBLEMS_STATUS'")
    op.execute("UPDATE notice SET category = 'USER_TIER' WHERE category = 'USER_TIER_STATUS'")

    # 3. 구 값 제거 (신 값만 남김)
    op.execute(
        "ALTER TABLE notice MODIFY COLUMN category ENUM("
        "'STUDY_INVITATION', 'STUDY_APPLICATION', 'STUDY_PROBLEM',"
        "'USER_PROBLEM', 'USER_TIER', 'SYSTEM_ANNOUNCEMENT'"
        ") NOT NULL"
    )

    # 4. category_detail 컬럼 추가
    op.add_column('notice', sa.Column('category_detail', sa.String(50), nullable=True))

    # 5. title 컬럼 제거
    op.drop_column('notice', 'title')


def downgrade() -> None:
    # title 컬럼 복원
    op.add_column('notice', sa.Column('title', sa.String(200), nullable=False, server_default=''))

    # category_detail 컬럼 제거
    op.drop_column('notice', 'category_detail')

    # category enum 되돌리기
    op.execute(
        "ALTER TABLE notice MODIFY COLUMN category ENUM("
        "'STUDY_INVITATION_STATUS', 'STUDY_APPLICATION_STATUS', 'STUDY_PROBLEMS_STATUS', "
        "'USER_PROBLEMS_STATUS', 'USER_TIER_STATUS', 'SYSTEM_ANNOUNCEMENT'"
        ") NOT NULL"
    )

    op.execute("UPDATE notice SET category = 'STUDY_INVITATION_STATUS' WHERE category = 'STUDY_INVITATION'")
    op.execute("UPDATE notice SET category = 'STUDY_APPLICATION_STATUS' WHERE category = 'STUDY_APPLICATION'")
    op.execute("UPDATE notice SET category = 'STUDY_PROBLEMS_STATUS' WHERE category = 'STUDY_PROBLEM'")
    op.execute("UPDATE notice SET category = 'USER_PROBLEMS_STATUS' WHERE category = 'USER_PROBLEM'")
    op.execute("UPDATE notice SET category = 'USER_TIER_STATUS' WHERE category = 'USER_TIER'")
