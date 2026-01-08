from pydantic import BaseModel, Field

from app.target.domain.entity.target import Target

class TargetQuery(BaseModel):
    """목표 정보"""
    target_id: int = Field(..., description="타겟 ID")
    target_code: str = Field(..., description="타겟 코드")
    target_display_name: str = Field(..., description="타겟 표시 이름")
    
    @classmethod
    def from_entity(cls, target: Target) -> 'TargetQuery':
        return cls(
            target_id=target.target_id.value,
            target_code=target.code,
            target_display_name=target.display_name
        )