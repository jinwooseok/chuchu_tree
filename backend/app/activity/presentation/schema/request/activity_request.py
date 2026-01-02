from pydantic import BaseModel, Field
from typing import List


class UpdateWillSolveProblemsRequest(BaseModel):
    """풀 문제 업데이트 요청"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    problem_id: List[int] = Field(..., alias="problemId", description="문제 ID 목록")

    class Config:
        populate_by_name = True


class UpdateSolvedProblemsRequest(BaseModel):
    """풀었던 문제 업데이트 요청"""
    date: str = Field(..., description="날짜 (YYYY-MM-DD)")
    problem_id: List[int] = Field(..., alias="problemId", description="문제 ID 목록")

    class Config:
        populate_by_name = True


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
