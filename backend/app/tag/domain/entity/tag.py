from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING

from app.common.domain.enums import ExcludedReason, TagLevel
from app.common.domain.vo.identifiers import TagId, TierId
from app.tag.domain.entity.tag_relation import TagRelation
from app.tag.domain.vo.tag_exclusion import TagExclusion
from app.common.domain.vo.primitives import TierRange

if TYPE_CHECKING:
    from app.target.domain.entity.target import Target

@dataclass
class Tag:
    """Aggregate Root - 태그"""
    tag_id: TagId|None
    code: str
    tag_display_name: str
    level: TagLevel
    exclusion: TagExclusion
    min_solved_person_count: int
    aliases: list[str]
    problem_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    parent_tag_relations: list[TagRelation] = field(default_factory=list)
    targets: list['Target'] = field(default_factory=list)
    
    @staticmethod
    def create(
        code: str,
        level: TagLevel,
        min_tier_id: TierId|None = None,
        max_tier_id: TierId|None = None
    ) -> 'Tag':
        """팩토리 메서드"""
        now = datetime.now()
        return Tag(
            tag_id=None,
            code=code,
            level=level,
            tag_display_name=None,
            exclusion=TagExclusion.is_not_excluded(),
            min_solved_person_count=0,
            aliases=[],
            problem_count=0,
            created_at=now,
            updated_at=now,
            deleted_at=None
        )
    
    def exclude(self, reason: ExcludedReason) -> None:
        """도메인 로직 - 태그 제외"""
        self.exclusion = TagExclusion.is_excluded(reason)
        self.updated_at = datetime.now()
    
    def include(self) -> None:
        """도메인 로직 - 태그 제외 해제"""
        self.exclusion = TagExclusion.is_not_excluded()
        self.updated_at = datetime.now()
    
    def add_parent_tag(self, sub_tag_id: TagId) -> None:
        """도메인 로직 - 하위 태그 추가"""
        if self.tag_id and self.tag_id.value == sub_tag_id.value:
            raise ValueError("Cannot add self as sub-tag")
        
        self.parent_tag_relations.append(TagRelation.create(self.tag_id, sub_tag_id))
        self.updated_at = datetime.now()
    
    def add_alias(self, alias: str) -> None:
        """도메인 로직 - 별칭 추가"""
        if alias not in self.aliases:
            self.aliases.append(alias)
            self.updated_at = datetime.now()
    
    def increment_problem_count(self) -> None:
        """도메인 로직 - 문제 수 증가"""
        self.problem_count += 1
        self.updated_at = datetime.now()
