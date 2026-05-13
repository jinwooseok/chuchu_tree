from dataclasses import dataclass

from app.common.domain.vo.identifiers import TierId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass(frozen=True)
class SkillRequirements:
    """Value Object - 숙련도 요구사항"""
    min_solved_problem: int
    min_user_tier: TierId
    min_solved_problem_tier: TierId
    
    def __post_init__(self):
        if self.min_solved_problem < 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
    
    def is_satisfied_by(
        self,
        solved_count: int,
        user_tier_id: TierId,
        max_solved_tier_id: TierId
    ) -> bool:
        """요구사항 충족 여부 확인"""
        if solved_count < self.min_solved_problem:
            return False
        if user_tier_id.value < self.min_user_tier.value:
            return False
        if max_solved_tier_id.value < self.min_solved_problem_tier.value:
            return False
        return True