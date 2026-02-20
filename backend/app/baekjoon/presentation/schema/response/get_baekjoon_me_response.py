from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.baekjoon.application.query.baekjoon_account_info_query import (
    BjAccountStatQuery,
    BjAccountQuery,
    UserAccountQuery,
    BaekjoonMeQuery
)
from app.baekjoon.presentation.schema.response.get_streaks_response import StreakItemResponse
from app.user.application.query.user_tags_query import TargetQuery

class BjAccountStatResponse(BaseModel):
    """백준 계정 통계 정보 응답"""
    tier_id: int = Field(..., description="현재 티어 ID")
    tier_name: str = Field(..., description="현재 티어 이름")
    longest_streak: int = Field(..., description="최장 스트릭")
    rating: int = Field(..., description="레이팅")
    class_level: int = Field(..., description="클래스 레벨", alias="class")
    tier_start_date: str | None = Field(None, description="현재 티어 시작 날짜")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: BjAccountStatQuery) -> "BjAccountStatResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            tier_id=query.tier_id,
            tier_name=query.tier_name,
            longest_streak=query.longest_streak,
            rating=query.rating,
            class_level=query.class_level,
            tier_start_date=query.tier_start_date.isoformat() if query.tier_start_date else None
        )


class BjAccountResponse(BaseModel):
    """백준 계정 정보 응답"""
    bj_account_id: str = Field(..., description="백준 계정 ID")
    stat: BjAccountStatResponse = Field(..., description="통계 정보")
    streaks: list[StreakItemResponse] = Field(..., description="스트릭 목록")
    registered_at: str = Field(..., description="등록일")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: BjAccountQuery) -> "BjAccountResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            bj_account_id=query.bj_account_id,
            stat=BjAccountStatResponse.from_query(query.stat),
            streaks=[StreakItemResponse.from_query(s) for s in query.streaks],
            registered_at=query.registered_at.isoformat()
        )

class TargetResponse(BaseModel):
    """목표 정보 쿼리 (/me용)"""
    target_id: int = Field(1, description="목표 ID")
    target_code: str = Field("DAILY", description="목표 코드")
    target_display_name: str = Field("DAILY", description="목표 표기")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: TargetQuery) -> "TargetResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            target_id=query.target_id,
            target_code=query.target_code,
            target_display_name=query.target_display_name
        )


class UserAccountResponse(BaseModel):
    """유저 계정 정보 응답"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    profile_image_url: str | None = Field(None, description="프로필 이미지 URL")
    target: TargetResponse | None = Field(None, description="목표 정보")
    registered_at: str = Field(..., description="가입일")
    is_synced: bool = Field(False, description="배치 동기화 완료 여부")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: UserAccountQuery) -> "UserAccountResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            user_account_id=query.user_account_id,
            profile_image_url=query.profile_image_url,
            target=TargetResponse.from_query(query.targets[0]) if query.targets else TargetResponse(),
            registered_at=query.registered_at.isoformat(),
            is_synced=query.is_synced,
        )


class GetBaekjoonMeResponse(BaseModel):
    """백준 /me 응답"""
    user_account: UserAccountResponse = Field(..., description="유저 계정 정보")
    bj_account: BjAccountResponse = Field(..., description="백준 계정 정보")
    linked_at: str = Field(..., description="계정 연동일")

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )

    @classmethod
    def from_query(cls, query: BaekjoonMeQuery) -> "GetBaekjoonMeResponse":
        """Query 객체로부터 Response 생성"""
        return cls(
            user_account=UserAccountResponse.from_query(query.user_account),
            bj_account=BjAccountResponse.from_query(query.bj_account),
            linked_at=query.linked_at.isoformat()
        )