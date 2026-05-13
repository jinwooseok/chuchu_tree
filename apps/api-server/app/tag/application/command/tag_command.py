from pydantic import BaseModel, Field

from app.common.domain.vo.identifiers import TagId


class GetTagInfoCommand(BaseModel):
    tag_id: TagId | None = Field(None)
    tag_code: str | None = Field(None)

class GetTagInfosCommand(BaseModel):
    """여러 태그 정보 조회 커맨드"""
    tag_ids: list[TagId] = Field(..., description="태그 ID 목록")