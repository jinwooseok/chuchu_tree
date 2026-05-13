from pydantic import BaseModel, Field


class GetTargetInfoPayload(BaseModel):
    target_id: int = Field(None, description="타겟 ID")
    target_code: str = Field(None, description="타겟 코드")
    
    
class GetTargetInfoResultPayload(BaseModel):
    target_id: int = Field(..., description="목표 ID")
    target_code: str = Field(..., description="목표 코드")
    target_display_name: str = Field(..., description="목표 표기")