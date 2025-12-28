from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import TierId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass
class Tier:
    """Entity - 티어 메타 정보"""
    tier_id: TierId
    tier_level: int
    tier_code: str
    tier_rating: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    
    @staticmethod
    def create(
        tier_id: TierId,
        tier_level: int,
        tier_code: str,
        tier_rating: int
    ) -> 'Tier':
        """팩토리 메서드"""
        if tier_level < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        if tier_rating < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        now = datetime.now()
        return Tier(
            tier_id=tier_id,
            tier_level=tier_level,
            tier_code=tier_code,
            tier_rating=tier_rating,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def update_rating(self, new_rating: int) -> None:
        """레이팅 업데이트"""
        if new_rating < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        self.tier_rating = new_rating
        self.updated_at = datetime.now()