# domain/target/domain/model/target.py
from dataclasses import dataclass, field
from datetime import datetime

from app.common.domain.vo.identifiers import TargetId, TagId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.target.domain.entity.target_tag import TargetTag


@dataclass
class Target:
    """Aggregate Root - 목표"""
    target_id: TargetId | None
    code: str
    display_name: str
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    required_tags: list['TargetTag'] = field(default_factory=list)
    
    @staticmethod
    def create(code: str, display_name: str) -> 'Target':
        """팩토리 메서드"""
        now = datetime.now()
        return Target(
            target_id=None,
            code=code,
            display_name=display_name,
            active=True,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            required_tags=[]
        )
    
    def add_required_tag(self, tag_id: TagId) -> None:
        """도메인 로직 - 필수 태그 추가"""
        if self._has_tag(tag_id):
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        self.required_tags.append(TargetTag.create(tag_id, self.target_id))
        self.updated_at = datetime.now()
    
    def remove_required_tag(self, tag_id: TagId) -> None:
        """도메인 로직 - 필수 태그 제거"""
        found = False
        for tag in self.required_tags:
            if tag.tag_id.value == tag_id.value and tag.active and tag.deleted_at is None:
                tag.deactivate()
                found = True
        
        if not found:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        self.updated_at = datetime.now()
    
    def activate(self) -> None:
        """도메인 로직 - 활성화"""
        self.active = True
        self.updated_at = datetime.now()
    
    def deactivate(self) -> None:
        """도메인 로직 - 비활성화"""
        self.active = False
        self.updated_at = datetime.now()
    
    def update_display_name(self, new_name: str) -> None:
        """도메인 로직 - 표시명 변경"""
        if not new_name or len(new_name.strip()) == 0:
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        self.display_name = new_name
        self.updated_at = datetime.now()
    
    def get_active_tags(self) -> list[TagId]:
        """활성화된 태그 ID 목록 조회"""
        return [
            tag.tag_id for tag in self.required_tags
            if tag.active and tag.deleted_at is None
        ]
    
    def _has_tag(self, tag_id: TagId) -> bool:
        return any(
            tag.tag_id.value == tag_id.value 
            and tag.active 
            and tag.deleted_at is None
            for tag in self.required_tags
        )
