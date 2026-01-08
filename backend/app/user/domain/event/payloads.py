from pydantic import BaseModel, Field


class GetTargetInfoPayload(BaseModel):
    target_code: str = Field(..., description="타겟 코드")