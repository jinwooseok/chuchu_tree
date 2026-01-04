"""Streak Entity - 스트릭 정보"""

from dataclasses import dataclass
from datetime import datetime, date

from app.common.domain.vo.identifiers import BaekjoonAccountId, StreakId


@dataclass
class Streak:
    """Entity - 날짜별 스트릭 정보"""
    streak_id: StreakId | None
    bj_account_id: BaekjoonAccountId
    streak_date: date
    solved_count: int
    created_at: datetime

    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        streak_date: date,
        solved_count: int
    ) -> 'Streak':
        return Streak(
            streak_id=None,  # DB에서 할당
            bj_account_id=bj_account_id,
            streak_date=streak_date,
            solved_count=solved_count,
            created_at=datetime.now()
        )

    def update_solved_count(self, count: int) -> None:
        """도메인 로직 - 해당 날짜의 푼 문제 수 업데이트"""
        self.solved_count = count
