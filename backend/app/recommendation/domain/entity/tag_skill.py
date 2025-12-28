from dataclasses import dataclass
from datetime import datetime

from app.common.domain.enums import SkillCode, TagLevel
from app.common.domain.vo.identifiers import TagSkillId, TierId
from app.recommendation.domain.vo.skill_requirements import SkillRequirements

@dataclass
class TagSkill:
    """Entity - 태그 숙련도"""
    tag_skill_id: TagSkillId | None
    tag_level: TagLevel
    skill_code: SkillCode
    requirements: SkillRequirements
    active: bool
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    
    @staticmethod
    def create(
        tag_level: TagLevel,
        skill_code: SkillCode,
        min_solved_problem: int,
        min_user_tier: TierId,
        min_solved_problem_tier: TierId
    ) -> 'TagSkill':
        """팩토리 메서드"""
        now = datetime.now()
        return TagSkill(
            tag_skill_id=None,
            tag_level=tag_level,
            skill_code=skill_code,
            requirements=SkillRequirements(
                min_solved_problem,
                min_user_tier,
                min_solved_problem_tier
            ),
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
    
    def update_requirements(
        self,
        min_solved_problem: int,
        min_user_tier: TierId,
        min_solved_problem_tier: TierId
    ) -> None:
        """요구사항 업데이트"""
        self.requirements = SkillRequirements(
            min_solved_problem,
            min_user_tier,
            min_solved_problem_tier
        )
        self.updated_at = datetime.now()