from dataclasses import dataclass
from datetime import datetime

from app.common.domain.enums import StudyMemberRole
from app.common.domain.vo.identifiers import StudyId, StudyMemberId, UserAccountId


@dataclass
class StudyMember:
    study_member_id: StudyMemberId | None
    study_id: StudyId | None
    user_account_id: UserAccountId
    role: StudyMemberRole
    joined_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
