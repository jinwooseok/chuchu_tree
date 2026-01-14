from dataclasses import dataclass

from pydantic import BaseModel, Field


class GetTagSummaryPayload(BaseModel):
    tag_code: str = Field(..., description="태그 코드")
    
class GetTagSummaryResultPayload(BaseModel):
    """태그 정보 요약 쿼리"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")