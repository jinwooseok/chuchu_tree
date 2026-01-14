"""태그별 계정 통계를 위한 Value Objects"""

from dataclasses import dataclass
from datetime import date

from app.common.domain.vo.identifiers import TagId, TierId


@dataclass(frozen=True)
class TagAccountStat:
    """태그별 유저 계정 통계 (영속성 없이 계산됨)"""

    tag_id: TagId
    solved_problem_count: int
    highest_tier_id: TierId | None
    last_solved_date: date | None

    @staticmethod
    def empty(tag_id: TagId) -> 'TagAccountStat':
        """빈 통계 생성 (해당 태그로 푼 문제가 없는 경우)"""
        return TagAccountStat(
            tag_id=tag_id,
            solved_problem_count=0,
            highest_tier_id=None,
            last_solved_date=None
        )
