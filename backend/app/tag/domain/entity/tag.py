from dataclasses import dataclass, field
from datetime import datetime

from app.common.domain.vo.identifiers import TagId, TierId
from app.tag.domain.entity.tag_relation import TagRelation
from app.tag.domain.enums import ExcludedReason, TagLevel
from app.tag.domain.vo.tag_exclusion import TagExclusion
from app.tag.domain.vo.tier_range import TierRange

@dataclass
class Tag:
    """Aggregate Root - 태그"""
    tag_id: TagId|None
    code: str
    level: TagLevel
    exclusion: TagExclusion
    applicable_tier_range: TierRange
    min_solved_person_count: int
    aliases: list[str]
    problem_count: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    sub_tags: list[TagRelation] = field(default_factory=list)
    
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
            exclusion=TagExclusion.not_excluded(),
            applicable_tier_range=TierRange(min_tier_id, max_tier_id),
            min_solved_person_count=0,
            aliases=[],
            problem_count=0,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            sub_tags=[]
        )
    
    def exclude(self, reason: ExcludedReason) -> None:
        """도메인 로직 - 태그 제외"""
        self.exclusion = TagExclusion.excluded(reason)
        self.updated_at = datetime.now()
    
    def include(self) -> None:
        """도메인 로직 - 태그 제외 해제"""
        self.exclusion = TagExclusion.not_excluded()
        self.updated_at = datetime.now()
    
    def add_sub_tag(self, sub_tag_id: TagId) -> None:
        """도메인 로직 - 하위 태그 추가"""
        if self.tag_id and self.tag_id.value == sub_tag_id.value:
            raise ValueError("Cannot add self as sub-tag")
        
        if self._has_sub_tag(sub_tag_id):
            raise ValueError(f"Sub-tag already exists: {sub_tag_id.value}")
        
        self.sub_tags.append(TagRelation.create(self.tag_id, sub_tag_id))
        self.updated_at = datetime.now()
    
    def remove_sub_tag(self, sub_tag_id: TagId) -> None:
        """도메인 로직 - 하위 태그 제거"""
        for relation in self.sub_tags:
            if relation.sub_tag_id.value == sub_tag_id.value:
                relation.deactivate()
        self.updated_at = datetime.now()
    
    def is_applicable_for_tier(self, tier_id: TierId) -> bool:
        """도메인 로직 - 특정 티어에 적용 가능한지 확인"""
        return self.applicable_tier_range.contains(tier_id)
    
    def add_alias(self, alias: str) -> None:
        """도메인 로직 - 별칭 추가"""
        if alias not in self.aliases:
            self.aliases.append(alias)
            self.updated_at = datetime.now()
    
    def increment_problem_count(self) -> None:
        """도메인 로직 - 문제 수 증가"""
        self.problem_count += 1
        self.updated_at = datetime.now()
    
    def _has_sub_tag(self, sub_tag_id: TagId) -> bool:
        return any(
            relation.sub_tag_id.value == sub_tag_id.value and relation.active
            for relation in self.sub_tags
        )
