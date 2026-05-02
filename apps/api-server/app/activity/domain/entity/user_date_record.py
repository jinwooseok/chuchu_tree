"""UserDateRecord Entity - 유저 단위 날짜별 풀이 수 기록 (streak 대체재)"""

from dataclasses import dataclass
from datetime import date, datetime

from app.common.domain.vo.identifiers import UserAccountId, UserDateRecordId


@dataclass
class UserDateRecord:
    """Entity - 유저가 특정 날짜에 푼 문제 수 기록

    - streak 테이블을 대체하는 유저 단위 날짜 추적 테이블
    - SOLVED만 추적 (WILL_SOLVE 무관)
    - user_account + bj_account 단위 (계정 변경 시 데이터 분리)
    """
    user_date_record_id: UserDateRecordId | None
    user_account_id: UserAccountId
    bj_account_id: str
    marked_date: date
    solved_count: int
    created_at: datetime
    updated_at: datetime

    @staticmethod
    def create(
        user_account_id: UserAccountId,
        bj_account_id: str,
        marked_date: date,
        solved_count: int
    ) -> 'UserDateRecord':
        now = datetime.now()
        return UserDateRecord(
            user_date_record_id=None,
            user_account_id=user_account_id,
            bj_account_id=bj_account_id,
            marked_date=marked_date,
            solved_count=solved_count,
            created_at=now,
            updated_at=now
        )

    def add_count(self, count: int) -> None:
        """도메인 로직 - 해당 날짜의 푼 문제 수 증가"""
        self.solved_count += count
        self.updated_at = datetime.now()

    def set_count(self, count: int) -> None:
        """도메인 로직 - 해당 날짜의 푼 문제 수 설정"""
        self.solved_count = count
        self.updated_at = datetime.now()
