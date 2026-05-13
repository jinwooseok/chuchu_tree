from dataclasses import dataclass
from datetime import datetime
from app.common.domain.vo.identifiers import TagId


@dataclass
class TagRelation:
    """Entity - 태그 관계"""
    tag_relation_id: int|None
    leading_tag_id: TagId
    sub_tag_id: TagId
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    
    @staticmethod
    def create(leading_tag_id: TagId, sub_tag_id: TagId) -> 'TagRelation':
        now = datetime.now()
        return TagRelation(
            tag_relation_id=None,
            leading_tag_id=leading_tag_id,
            sub_tag_id=sub_tag_id,
            active=True,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def deactivate(self) -> None:
        """비활성화"""
        self.active = False
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """활성화"""
        self.active = True
        self.updated_at = datetime.now()