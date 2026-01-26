# domain/problem/domain/model/problem.py
from dataclasses import dataclass, field
from datetime import datetime

from app.common.domain.vo.identifiers import ProblemId, TagId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.problem.domain.entity.problem_tag import ProblemTag
from app.problem.domain.entity.problem_update_history import ProblemUpdateHistory
from app.common.domain.vo.primitives import TierLevel

@dataclass
class Problem:
    """Aggregate Root - 문제"""
    problem_id: ProblemId
    title: str
    tier_level: TierLevel
    class_level: int|None
    solved_user_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    tags: list[ProblemTag] = field(default_factory=list)
    update_histories: list[ProblemUpdateHistory] = field(default_factory=list)
    
    @staticmethod
    def create(
        problem_id: ProblemId,
        title: str,
        tier_level: TierLevel,
        solved_user_count: int,
        class_level: int|None = None
    ) -> 'Problem':
        """팩토리 메서드"""
        now = datetime.now()
        return Problem(
            problem_id=problem_id,
            title=title,
            tier_level=tier_level,
            class_level=class_level,
            solved_user_count=solved_user_count,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            tags=[],
            update_histories=[]
        )
    
    def update_tier_level(self, new_tier_level: TierLevel) -> None:
        """도메인 로직 - 티어 레벨 변경"""
        if self.tier_level.value == new_tier_level.value:
            return
        
        self._record_update("tier_level", self.tier_level.value, new_tier_level.value)
        self.tier_level = new_tier_level
        self.updated_at = datetime.now()
    
    def update_title(self, new_title: str) -> None:
        """도메인 로직 - 제목 변경"""
        if self.title == new_title:
            return
        
        self._record_update("title", self.title, new_title)
        self.title = new_title
        self.updated_at = datetime.now()
    
    def add_tag(self, tag_id: TagId) -> None:
        """도메인 로직 - 태그 추가"""
        if self._has_tag(tag_id):
            raise APIException(ErrorCode.INVALID_INPUT_VALUE)
        
        self.tags.append(ProblemTag.create(self.problem_id, tag_id))
        self.updated_at = datetime.now()
    
    def remove_tag(self, tag_id: 'TagId') -> None:
        """도메인 로직 - 태그 제거"""
        self.tags = [tag for tag in self.tags if tag.tag_id.value != tag_id.value]
        self.updated_at = datetime.now()
    
    def has_any_tag(self, tag_ids: list[TagId]) -> bool:
        """도메인 로직 - 특정 태그 중 하나라도 가지고 있는지 확인"""
        problem_tag_ids = {tag.tag_id.value for tag in self.tags}
        return any(tag_id.value in problem_tag_ids for tag_id in tag_ids)
    
    def _has_tag(self, tag_id: TagId) -> bool:
        return any(tag.tag_id.value == tag_id.value for tag in self.tags)
    
    def _record_update(self, field: str, old_value: any, new_value: any) -> None:
        """변경 이력 기록"""
        self.update_histories.append(
            ProblemUpdateHistory.create(self.problem_id, field, old_value, new_value)
        )