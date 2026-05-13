from datetime import date
from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.baekjoon.application.query.streaks_query import StreakItemQuery, StreaksQuery


class StreakItemResponse(BaseModel):
    """스트릭 항목 응답"""
    problem_history_id: int | None = Field(None, description="연관 문제 ID")
    streak_date: str = Field(..., description="스트릭 날짜")
    solved_count: int = Field(..., description="해당 날짜에 푼 문제 수")
    solved_level: int = Field(..., description="푼 문제 수에 따른 레벨")
    
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: StreakItemQuery) -> "StreakItemResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            problem_history_id=query.problem_history_id,
            streak_date=query.streak_date.isoformat(),
            solved_count=query.solved_count,
            solved_level=cls._calculate_level(query.solved_count)
        )
    
    @staticmethod
    def _calculate_level(count: int) -> int:
        """푼 문제 수에 따른 레벨 계산 규칙 적용"""
        if count <= 0:
            return 0
        if count == 1:
            return 1
        if count == 2:
            return 2
        if 3 <= count <= 4:
            return 3
        return 4 # 5개 이상

class GetStreaksResponse(BaseModel):
    """스트릭 목록 응답"""
    bj_account_id: str = Field(..., description="백준 계정 ID")
    streaks: list[StreakItemResponse] = Field(..., description="스트릭 목록")
    total_count: int = Field(..., description="전체 스트릭 수")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: StreaksQuery) -> "GetStreaksResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            bj_account_id=query.bj_account_id,
            streaks=[StreakItemResponse.from_query(streak) for streak in query.streaks],
            total_count=query.total_count
        )