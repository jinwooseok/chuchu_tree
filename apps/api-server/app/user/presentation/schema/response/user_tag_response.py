"""유저 태그 목록 Response Schema"""

from pydantic import BaseModel, Field

from app.user.application.query.user_tags_query import (
    AccountStatQuery,
    CategoryQuery,
    NextLevelStatQuery,
    PrevTagQuery,
    RequiredStatQuery,
    TagAliasQuery,
    TargetQuery,
    UserTagDetailQuery,
    UserTagsQuery
)


class PrevTagResponse(BaseModel):
    """선수 태그 정보"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    satisfied_yn: bool = Field(..., alias="satisfiedYn")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: PrevTagQuery) -> 'PrevTagResponse':
        """Query를 Response로 변환"""
        return cls(
            tag_id=query.tag_id,
            tag_code=query.tag_code,
            tag_display_name=query.tag_display_name,
            satisfied_yn=query.satisfied_yn
        )


class RequiredStatResponse(BaseModel):
    """태그 해금 요구사항"""
    required_min_tier: int = Field(..., alias="requiredMinTier")
    prev_tags: list[PrevTagResponse] = Field(..., alias="prevTags")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: RequiredStatQuery) -> 'RequiredStatResponse':
        """Query를 Response로 변환"""
        return cls(
            required_min_tier=query.required_min_tier,
            prev_tags=[PrevTagResponse.from_query(prev) for prev in query.prev_tags]
        )


class NextLevelStatResponse(BaseModel):
    """다음 레벨 요구사항"""
    next_level: str = Field(..., alias="nextLevel")
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    required_min_tier: int = Field(..., alias="requiredMinTier")
    higher_problem_tier: int = Field(..., alias="higherProblemTier")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: NextLevelStatQuery) -> 'NextLevelStatResponse':
        """Query를 Response로 변환"""
        return cls(
            next_level=query.next_level,
            solved_problem_count=query.solved_problem_count,
            required_min_tier=query.required_min_tier,
            higher_problem_tier=query.higher_problem_tier
        )


class AccountStatResponse(BaseModel):
    """유저의 태그별 통계"""
    current_level: str = Field(..., alias="currentLevel")
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    required_min_tier: int | None = Field(None, alias="requiredMinTier")
    higher_problem_tier: int | None = Field(None, alias="higherProblemTier")
    last_solved_date: str | None = Field(None, alias="lastSolvedDate")
    recommendation_period: int = Field(..., alias="recommendation_period")
    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: AccountStatQuery) -> 'AccountStatResponse':
        """Query를 Response로 변환"""
        period = 3
        if query.current_level == "ADVANCED":
            period = 7
        elif query.current_level == "MASTER":
            period = 14
            
        return cls(
            current_level=query.current_level,
            solved_problem_count=query.solved_problem_count,
            required_min_tier=query.required_min_tier,
            higher_problem_tier=query.higher_problem_tier,
            last_solved_date=query.last_solved_date.isoformat() if query.last_solved_date else None,
            recommendation_period=period
        )


class TagAliasResponse(BaseModel):
    """태그 별칭"""
    alias: str

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: TagAliasQuery) -> 'TagAliasResponse':
        """Query를 Response로 변환"""
        return cls(alias=query.alias)


class TargetResponse(BaseModel):
    """목표 정보"""
    target_id: int = Field(..., alias="targetId")
    target_code: str = Field(..., alias="targetCode")
    target_display_name: str = Field(..., alias="targetDisplayName")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: TargetQuery) -> 'TargetResponse':
        """Query를 Response로 변환"""
        return cls(
            target_id=query.target_id,
            target_code=query.target_code,
            target_display_name=query.target_display_name
        )

class UserTagSummaryResponse(BaseModel):
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    
    class Config:
        populate_by_name = True
    
    @classmethod
    def from_query(cls, query: UserTagDetailQuery) -> 'UserTagSummaryResponse':
        return cls(
                tag_id=query.tag_id,
                tag_code=query.tag_code,
                tag_display_name=query.tag_display_name
        )
    
class UserTagDetailResponse(BaseModel):
    """유저 태그 상세 정보"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    tag_targets: list[TargetResponse] = Field(..., alias="tagTargets")
    tag_aliases: list[TagAliasResponse] = Field(..., alias="tagAliases")
    required_stat: RequiredStatResponse | None = Field(None, alias="requiredStat")
    next_level_stat: NextLevelStatResponse | None = Field(None, alias="nextLevelStat")
    account_stat: AccountStatResponse = Field(..., alias="accountStat")
    locked_yn: bool = Field(..., alias="lockedYn")
    excluded_yn: bool = Field(..., alias="excludedYn")
    recommendation_yn: bool = Field(..., alias="recommendationYn")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: UserTagDetailQuery) -> 'UserTagDetailResponse':
        """Query를 Response로 변환"""
        return cls(
            tag_id=query.tag_id,
            tag_code=query.tag_code,
            tag_display_name=query.tag_display_name,
            tag_targets=[TargetResponse.from_query(target) for target in query.tag_targets],
            tag_aliases=[TagAliasResponse.from_query(alias) for alias in query.tag_aliases],
            required_stat=RequiredStatResponse.from_query(query.required_stat) if query.required_stat else None,
            next_level_stat=NextLevelStatResponse.from_query(query.next_level_stat) if query.next_level_stat else None,
            account_stat=AccountStatResponse.from_query(query.account_stat),
            locked_yn=query.locked_yn,
            excluded_yn=query.excluded_yn,
            recommendation_yn=query.recommendation_yn
        )


class CategoryResponse(BaseModel):
    """태그 카테고리"""
    category_name: str = Field(..., alias="categoryName")
    tags: list[UserTagSummaryResponse]

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: CategoryQuery) -> 'CategoryResponse':
        """Query를 Response로 변환"""
        return cls(
            category_name=query.category_name,
            tags=[UserTagSummaryResponse.from_query(tag) for tag in query.tags]
        )


class UserTagsResponse(BaseModel):
    """유저 태그 목록 조회 응답"""
    categories: list[CategoryResponse]
    tags: list[UserTagDetailResponse]

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: UserTagsQuery) -> 'UserTagsResponse':
        """Query를 Response로 변환"""
        return cls(
            categories=[CategoryResponse.from_query(cat) for cat in query.categories],
            tags=[UserTagDetailResponse.from_query(tag) for tag in query.tags]
        )
