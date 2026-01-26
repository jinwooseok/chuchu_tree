from dataclasses import dataclass
from datetime import datetime

from app.common.domain.enums import FilterCode
from app.common.domain.vo.identifiers import LevelFilterId, TagSkillId, TierId
from app.common.domain.vo.primitives import TierLevel, TierRange
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass
class LevelFilter:
    """Aggregate Root - 문제 추천 난이도 필터"""
    filter_id: LevelFilterId | None
    filter_code: FilterCode
    display_name: str
    max_user_tier_diff: int | None
    min_user_tier_diff: int | None
    tag_skill_code: str
    min_tag_skill_rate: int
    max_tag_skill_rate: int
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    
    @staticmethod
    def create(
        filter_code: FilterCode,
        display_name: str,
        tag_skill_code: str,
        min_tag_skill_rate: int,
        max_tag_skill_rate: int,
        max_user_tier_diff: int | None = None,
        min_user_tier_diff: int | None = None
    ) -> 'LevelFilter':
        """팩토리 메서드"""
        # 티어 차이 검증
        if max_user_tier_diff is not None and min_user_tier_diff is not None:
            if min_user_tier_diff > max_user_tier_diff:
                raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        # 숙련도 비율 검증
        if max_tag_skill_rate < 0 or min_tag_skill_rate > 100:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        now = datetime.now()
        return LevelFilter(
            filter_id=None,
            filter_code=filter_code,
            display_name=display_name,
            max_user_tier_diff=max_user_tier_diff,
            min_user_tier_diff=min_user_tier_diff,
            tag_skill_code=tag_skill_code,
            min_tag_skill_rate=min_tag_skill_rate,
            max_tag_skill_rate=max_tag_skill_rate,
            active=True,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def calculate_tier_range(self, user_tier: TierLevel) -> TierRange:
        """도메인 로직 - 유저 티어 기반 추천 티어 범위 계산"""
        min_tier = None
        max_tier = None
        
        if self.min_user_tier_diff is not None:
            min_value = user_tier.value + self.min_user_tier_diff
            min_tier = TierLevel(max(0, min_value))
        
        if self.max_user_tier_diff is not None:
            max_value = user_tier.value + self.max_user_tier_diff
            max_tier = TierLevel(max(0, max_value))
        
        return TierRange(
            min_tier_id=TierId(min_tier.value) if min_tier else None,
            max_tier_id=TierId(max_tier.value) if max_tier else None
        )
    
    def activate(self) -> None:
        """활성화"""
        self.active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """비활성화"""
        self.active = False
        self.updated_at = datetime.now()
    
    def update_tier_diff_range(
        self,
        min_diff: int | None,
        max_diff: int | None
    ) -> None:
        """티어 차이 범위 업데이트"""
        if min_diff is not None and max_diff is not None:
            if min_diff > max_diff:
                raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        self.min_user_tier_diff = min_diff
        self.max_user_tier_diff = max_diff
        self.updated_at = datetime.now()
    
    def update_tag_skill_rate(self, new_rate: int) -> None:
        """태그 숙련도 비율 업데이트"""
        if new_rate < 0 or new_rate > 100:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        self.tag_skill_rate = new_rate
        self.updated_at = datetime.now()