from pydantic import BaseModel, Field

from app.activity.application.query.banned_list_query import BannedProblemsQuery, BannedTagsQuery, TagInfoQuery


class ProblemRecordResponse(BaseModel):
    """문제 기록 조회 응답"""
    memo_title: str = Field(..., alias="memoTitle", description="메모 제목")
    content: str = Field(..., description="내용")

    class Config:
        populate_by_name = True


class TagInfoResponse(BaseModel):
    """태그 정보 응답"""
    tag_id: int = Field(..., alias="tagId", description="태그 ID")
    tag_code: str = Field(..., alias="tagCode", description="태그 코드")
    tag_display_name: str = Field(..., alias="tagDisplayName", description="태그 표시 이름")

    class Config:
        populate_by_name = True


class ProblemInfoResponse(BaseModel):
    """문제 정보 응답"""
    problem_id: int = Field(..., alias="problemId", description="문제 ID")
    problem_title: str = Field(..., alias="problemTitle", description="문제 제목")
    problem_tier_level: int = Field(..., alias="problemTierLevel", description="문제 티어 레벨")
    problem_tier_name: str = Field(..., alias="problemTierName", description="문제 티어 이름")
    problem_class_level: int | None = Field(None, alias="problemClassLevel", description="문제 클래스 레벨")
    tags: list[TagInfoResponse] = Field(default_factory=list, description="태그 목록")

    class Config:
        populate_by_name = True


class BannedProblemsResponse(BaseModel):
    """밴된 문제 목록 응답"""
    banned_problem_list: list[ProblemInfoResponse] = Field(..., alias="bannedProblems", description="밴된 문제 목록")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: BannedProblemsQuery) -> dict:
        """Query를 Response로 변환"""
        problems = [
            ProblemInfoResponse(
                problem_id=p.problem_id,
                problem_title=p.problem_title,
                problem_tier_level=p.problem_tier_level,
                problem_tier_name=p.problem_tier_name,
                problem_class_level=p.problem_class_level,
                tags=[
                    TagInfoResponse(
                        tag_id=t.tag_id,
                        tag_code=t.tag_code,
                        tag_display_name=t.tag_display_name
                    )
                    for t in p.tags
                ]
            )
            for p in query.banned_problem_list
        ]
        return cls(banned_problem_list=problems).model_dump(by_alias=True)


class BannedTagsResponse(BaseModel):
    """밴된 태그 목록 응답"""
    banned_tag_list: list[TagInfoResponse] = Field(..., alias="bannedTags", description="밴된 태그 목록")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: BannedTagsQuery) -> dict:
        """Query를 Response로 변환"""
        tags = [
            TagInfoResponse(
                tag_id=t.tag_id,
                tag_code=t.tag_code,
                tag_display_name=t.tag_display_name
            )
            for t in query.banned_tag_list
        ]
        return cls(banned_tag_list=tags).model_dump(by_alias=True)
