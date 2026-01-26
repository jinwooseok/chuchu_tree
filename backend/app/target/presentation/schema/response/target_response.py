from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.target.application.query.target_query import TargetQuery


class TargetItem(BaseModel):
    """목표 항목"""
    target_id: int = Field(..., alias="targetId")
    target_code: str = Field(..., alias="targetCode")
    target_display_name: str = Field(..., alias="targetDisplayName")

    class Config:
        populate_by_name = True

class AllTargetsResponse(BaseModel):
    """모든 목표 조회 응답"""
    targets: list[TargetItem]

    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True
    )
        
    @staticmethod
    def from_queries(queries: list[TargetQuery])-> 'AllTargetsResponse':
        return AllTargetsResponse(
            targets = [TargetItem(
                target_id = query.target_id,
                target_code = query.target_code,
                target_display_name = query.target_display_name
            ) for query in queries]
        )
