from dataclasses import dataclass
from datetime import date, datetime

from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemHistoryId, ProblemId


@dataclass
class ProblemHistory:
    """Entity - 문제 해결 히스토리 (bj_account 단위, 날짜 정보 없음)"""
    problem_history_id: ProblemHistoryId | None
    bj_account_id: BaekjoonAccountId
    problem_id: ProblemId
    created_at: datetime
    solved_date: date | None = None  # 연동 시 solved.ac에서 받은 날짜 (참고용)

    @staticmethod
    def create(
        bj_account_id: BaekjoonAccountId,
        problem_id: ProblemId,
        solved_date: date | None = None
    ) -> 'ProblemHistory':
        """문제 풀이 기록 생성"""
        return ProblemHistory(
            problem_history_id=None,  # DB에서 할당
            bj_account_id=bj_account_id,
            problem_id=problem_id,
            solved_date=solved_date,
            created_at=datetime.now()
        )
