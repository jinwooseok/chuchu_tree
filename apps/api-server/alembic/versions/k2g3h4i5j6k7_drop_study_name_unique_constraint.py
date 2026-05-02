"""drop_study_name_unique_constraint

Revision ID: k2g3h4i5j6k7
Revises: j1f2a3b4c5d6
Create Date: 2026-03-11 00:00:00.000000

변경 내용:
1. study.uk_study_name 유니크 제약 제거
   - soft-delete된 스터디 이름을 재사용할 수 있도록 변경
   - 활성 스터디 간 이름 중복 방지는 application layer(is_name_taken)에서 처리
"""
from typing import Sequence, Union

from alembic import op


revision: str = 'k2g3h4i5j6k7'
down_revision: Union[str, None] = 'j1f2a3b4c5d6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_constraint('uk_study_name', 'study', type_='unique')


def downgrade() -> None:
    op.create_unique_constraint('uk_study_name', 'study', ['study_name'])
