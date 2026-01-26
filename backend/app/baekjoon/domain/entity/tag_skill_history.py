from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import BaekjoonAccountId, TagId, TagSkillId

@dataclass
class TagSkillHistory:
    """Entity - 태그 숙련도 변경 히스토리"""
    tag_skill_history_id: int|None
    bj_account_id: BaekjoonAccountId
    tag_id: TagId
    prev_skill_id: TagSkillId|None
    changed_skill_id: TagSkillId
    changed_at: datetime
    created_at: datetime
    
    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        tag_id: TagId,
        changed_skill_id: TagSkillId,
        prev_skill_id: TagSkillId|None = None
    ) -> 'TagSkillHistory':
        now = datetime.now()
        return TagSkillHistory(
            tag_skill_history_id=None,
            bj_account_id=bj_account_id,
            tag_id=tag_id,
            prev_skill_id=prev_skill_id,
            changed_skill_id=changed_skill_id,
            changed_at=now,
            created_at=now
        )