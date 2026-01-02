from pydantic import BaseModel, Field


class ProblemRecordResponse(BaseModel):
    """문제 기록 조회 응답"""
    memo_title: str = Field(..., alias="memoTitle", description="메모 제목")
    content: str = Field(..., description="내용")

    class Config:
        populate_by_name = True
