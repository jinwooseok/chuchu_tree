from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemHistoryId, ProblemId, StreakId


@dataclass
class ProblemHistory:
    """Entity - 문제 해결 히스토리 (시간 정보 없음, streak과 나중에 연동)"""
    problem_history_id: ProblemHistoryId | None
    bj_account_id: BaekjoonAccountId
    problem_id: ProblemId
    streak_id: StreakId | None  # 나중에 연동
    created_at: datetime

    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        problem_id: ProblemId
    ) -> 'ProblemHistory':
        """문제 풀이 기록 생성 (처음엔 시간 정보 없음)"""
        return ProblemHistory(
            problem_history_id=None,  # DB에서 할당
            bj_account_id=bj_account_id,
            problem_id=problem_id,
            streak_id=None,  # 나중에 연동
            created_at=datetime.now()
        )

    def link_to_streak(self, streak_id: StreakId) -> None:
        """도메인 로직 - 스트릭과 연동"""
        self.streak_id = streak_id