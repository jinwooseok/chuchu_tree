"""문제 정보 조회 요청 페이로드"""
from pydantic import BaseModel, Field


class GetProblemsInfoPayload(BaseModel):
    """문제 정보 조회 요청 페이로드"""
    problem_ids: list[int] = Field(..., description="문제 ID 목록")
