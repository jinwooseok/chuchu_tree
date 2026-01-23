from pydantic import BaseModel, Field
from datetime import date as date_

class UpdateWillSolveProblemsRequest(BaseModel):
    """풀 문제 업데이트 요청"""
    date: date_ = Field(..., description="날짜 (YYYY-MM-DD)")
    problem_ids: list[int] = Field(..., alias="problemIds", description="문제 ID 목록")

    class Config:
        populate_by_name = True


class UpdateSolvedProblemsRequest(BaseModel):
    """풀었던 문제 업데이트 요청"""
    date: date_ = Field(..., description="날짜 (YYYY-MM-DD)")
    problem_ids: list[int] = Field(..., alias="problemId", description="문제 ID 목록")

    class Config:
        populate_by_name = True

class UpdateSolvedAndWillSolveProblemsRequest(BaseModel):
    date: date_ = Field(..., description="날짜 (YYYY-MM-DD)")
    solved_problem_ids: list[int] = Field(..., description="풀었던 문제 ID 목록")
    will_solve_problem_ids: list[int] = Field(..., description="풀 예정 문제 ID 목록")

class ProblemRecordRequest(BaseModel):
    """문제 기록 생성/업데이트 요청"""
    problem_id: int = Field(..., alias="problemId", description="문제 ID")
    memo_title: str = Field(..., alias="memoTitle", description="메모 제목")
    content: str = Field(..., description="내용")

    class Config:
        populate_by_name = True


class BanProblemRequest(BaseModel):
    """문제 밴 요청"""
    problem_id: int = Field(..., alias="problemId", description="문제 ID")

    class Config:
        populate_by_name = True


class BanTagRequest(BaseModel):
    """태그 밴 요청"""
    tag_code: str = Field(..., alias="tagCode", description="태그 코드")

    class Config:
        populate_by_name = True


class SetRepresentativeTagRequest(BaseModel):
    """대표 태그 설정 요청"""
    representative_tag_code: str | None = Field(None, alias="representativeTagCode", description="대표 태그 코드 (null이면 대표 태그 해제)")

    class Config:
        populate_by_name = True
