from dataclasses import dataclass

from pydantic import BaseModel, Field

from app.common.domain.vo.identifiers import TagId


class GetTagSummaryPayload(BaseModel):
    tag_code: str = Field(..., description="태그 코드")

class GetTagSummaryResultPayload(BaseModel):
    """태그 정보 요약 쿼리"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")
    
class GetTagSummarysPayload(BaseModel):
    tag_ids: list[TagId] = Field(..., description="태그 ID 목록")

class GetTagSummarysResultPayload(BaseModel):
    """태그 정보 요약 쿼리"""
    tags: list[GetTagSummaryResultPayload] = Field(..., description="태그 목록")
    
class GetProblemsInfoPayload(BaseModel):
    """문제 정보 조회 요청 페이로드"""
    problem_ids: list[int] = Field(..., description="문제 ID 목록")