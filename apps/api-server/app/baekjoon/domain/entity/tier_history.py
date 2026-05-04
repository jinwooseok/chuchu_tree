from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import BaekjoonAccountId, TierId

@dataclass
class TierHistory:
    """Entity - 티어 변경 히스토리"""
    tier_history_id: int|None
    bj_account_id: BaekjoonAccountId
    prev_tier_id: TierId
    changed_tier_id: TierId
    changed_at: datetime
    created_at: datetime
    
    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        prev_tier_id: TierId,
        changed_tier_id: TierId
    ) -> 'TierHistory':
        now = datetime.now()
        return TierHistory(
            tier_history_id=None,
            bj_account_id=bj_account_id,
            prev_tier_id=prev_tier_id,
            changed_tier_id=changed_tier_id,
            changed_at=now,
            created_at=now
        )