from dataclasses import dataclass
from datetime import date, datetime

from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemHistoryId, ProblemId, StreakId


@dataclass
class ProblemHistory:
    """Entity - 문제 해결 히스토리 (시간 정보 없음, streak과 나중에 연동)"""
    problem_history_id: ProblemHistoryId | None
    bj_account_id: BaekjoonAccountId
    problem_id: ProblemId
    streak_id: StreakId | None  # 나중에 연동
    created_at: datetime
    solved_date: date | None = None
    streak_date: date | None = None  # streak과 연동된 경우 streak의 날짜

    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        problem_id: ProblemId,
        solved_date: date | None = None,
        streak_id: StreakId | None = None
    ) -> 'ProblemHistory':
        """문제 풀이 기록 생성 (처음엔 시간 정보 없음)"""
        return ProblemHistory(
            problem_history_id=None,  # DB에서 할당
            bj_account_id=bj_account_id,
            problem_id=problem_id,
            streak_id=streak_id,  
            solved_date=solved_date,
            created_at=datetime.now()
        )

    def link_to_streak(self, streak_id: StreakId) -> None:
        """도메인 로직 - 스트릭과 연동"""
        self.streak_id = streak_id