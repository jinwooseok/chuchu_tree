from pydantic import BaseModel, Field


class SetTargetRequest(BaseModel):
    """목표 설정 요청"""
    target_code: str = Field(..., alias="targetCode", description="목표 코드 (CT, DAILY, BEGINNER)")

    class Config:
        populate_by_name = True
