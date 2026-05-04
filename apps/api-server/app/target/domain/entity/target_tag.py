from dataclasses import dataclass
from datetime import datetime
from app.common.domain.vo.identifiers import TagId, TargetId


@dataclass
class TargetTag:
    """Entity - 목표별 태그"""
    target_tag_id: int | None
    tag_id: TagId
    target_id: TargetId
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    
    @staticmethod
    def create(tag_id: TagId, target_id: TargetId) -> 'TargetTag':
        """팩토리 메서드"""
        now = datetime.now()
        return TargetTag(
            target_tag_id=None,
            tag_id=tag_id,
            target_id=target_id,
            active=True,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def activate(self) -> None:
        """활성화"""
        self.active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """비활성화"""
        self.active = False
        self.updated_at = datetime.now()