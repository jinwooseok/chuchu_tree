from pydantic import BaseModel, Field

from app.tag.domain.entity.tag import Tag


class TagSummaryQuery(BaseModel):
    """태그 정보 요약 쿼리"""
    tag_id: int = Field(..., description="태그 ID")
    tag_code: str = Field(..., description="태그 코드")
    tag_display_name: str = Field(..., description="태그 표시 이름")

    @classmethod
    def from_entity(cls, tag:Tag) -> 'TagSummaryQuery':
        return cls(
            tag_id=tag.tag_id.value,
            tag_code=tag.code,
            tag_display_name=tag.tag_display_name
        )

class TagInfosQuery(BaseModel):
    """여러 태그 정보 조회 쿼리"""
    tags: list[TagSummaryQuery] = Field(..., description="태그 목록")