from datetime import datetime, date
from pydantic import BaseModel, Field

from app.baekjoon.application.query.streaks_query import StreakItemQuery


class BjAccountStatQuery(BaseModel):
    """백준 계정 통계 정보 쿼리"""
    tier_id: int = Field(..., description="현재 티어 ID")
    tier_name: str = Field(..., description="현재 티어 이름 (예: B5, S3)")
    longest_streak: int = Field(..., description="최장 스트릭")
    rating: int = Field(..., description="레이팅")
    class_level: int = Field(..., description="클래스 레벨")
    tier_start_date: date | None = Field(None, description="현재 티어 시작 날짜")


class BjAccountQuery(BaseModel):
    """백준 계정 정보 쿼리 (/me용)"""
    bj_account_id: str = Field(..., description="백준 계정 ID")
    stat: BjAccountStatQuery = Field(..., description="통계 정보")
    streaks: list[StreakItemQuery] = Field(..., description="스트릭 목록 (최근 365일)")
    registered_at: datetime = Field(..., description="등록일")

class TargetQuery(BaseModel):
    """목표 정보 쿼리 (/me용)"""
    target_id: int = Field(..., description="목표 ID")
    target_code: str = Field(..., description="목표 코드")
    target_display_name: str = Field(..., description="목표 표기")
    
class UserAccountQuery(BaseModel):
    """유저 계정 정보 쿼리 (/me용)"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    profile_image_url: str | None = Field(None, description="프로필 이미지 URL")
    targets: list[TargetQuery] = Field([], description="목표 목록")
    registered_at: datetime = Field(..., description="가입일")
    is_synced: bool = Field(False, description="배치 동기화 완료 여부")


class BaekjoonMeQuery(BaseModel):
    """백준 /me 통합 쿼리"""
    user_account: UserAccountQuery = Field(..., description="유저 계정 정보")
    bj_account: BjAccountQuery = Field(..., description="백준 계정 정보")
    linked_at: datetime = Field(..., description="계정 연동일")
