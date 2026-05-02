from pydantic import BaseModel, Field

class GetTargetInfoCommand(BaseModel):
    target_id: int | None = Field(None)
    target_code: str | None = Field(None)