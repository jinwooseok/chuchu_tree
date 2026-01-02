from pydantic import BaseModel, Field
from typing import List


class TargetItem(BaseModel):
    """목표 항목"""
    target_id: int = Field(..., alias="targetId")
    target_code: str = Field(..., alias="targetCode")
    target_display_name: str = Field(..., alias="targetDisplayName")

    class Config:
        populate_by_name = True


class UserTargetsResponse(BaseModel):
    """유저 목표 조회 응답"""
    targets: List[TargetItem]

    class Config:
        populate_by_name = True


class AllTargetsResponse(BaseModel):
    """모든 목표 조회 응답"""
    targets: List[TargetItem]

    class Config:
        populate_by_name = True
