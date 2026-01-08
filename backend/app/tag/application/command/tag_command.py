from pydantic import BaseModel, Field


class GetTagInfoCommand(BaseModel):
    tag_id: int | None = Field(None)
    tag_code: str | None = Field(None)