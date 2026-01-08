from dataclasses import dataclass

from app.target.domain.entity.target import Target


@dataclass
class TargetQuery:
    """목표 정보"""
    target_id: int
    target_code: str
    target_display_name: str
    
    @staticmethod
    def from_entity(targets: list[Target]):
        return [TargetQuery(
            target_id=target.target_id,
            target_code=target.code,
            target_display_name=target.display_name
        ) for target in targets]