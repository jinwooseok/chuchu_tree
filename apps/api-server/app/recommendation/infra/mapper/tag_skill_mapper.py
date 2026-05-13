"""TagSkill Mapper"""

from app.common.domain.enums import SkillCode, TagLevel
from app.common.domain.vo.identifiers import TagSkillId, TagId, TierId
from app.recommendation.domain.entity.tag_skill import TagSkill
from app.recommendation.domain.vo.skill_requirements import SkillRequirements
from app.recommendation.infra.model.tag_skill import TagSkillModel


class TagSkillMapper:
    """TagSkill Entity와 Model 간 변환"""

    @staticmethod
    def to_entity(model: TagSkillModel | None) -> TagSkill | None:
        """Model -> Entity"""
        if not model:
            return None

        requirements = SkillRequirements(
            min_solved_problem=model.min_solved_problem,
            min_user_tier=TierId(model.min_user_tier),
            min_solved_problem_tier=TierId(model.min_solved_problem_tier)
        )

        return TagSkill(
            tag_skill_id=TagSkillId(model.tag_skill_id),
            tag_id=TagId(model.tag_id) if model.tag_id else None,  # NEW
            tag_level=TagLevel(model.tag_level),
            skill_code=SkillCode(model.tag_skill_code),
            requirements=requirements,
            recommendation_period=model.recommendation_period,
            active=model.active_yn,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: TagSkill) -> TagSkillModel:
        """Entity -> Model"""
        return TagSkillModel(
            tag_skill_id=entity.tag_skill_id.value if entity.tag_skill_id else None,
            tag_id=entity.tag_id.value if entity.tag_id else None,  # NEW
            tag_level=entity.tag_level.value,
            tag_skill_code=entity.skill_code.value,
            min_solved_problem=entity.requirements.min_solved_problem,
            min_user_tier=entity.requirements.min_user_tier.value,
            min_solved_problem_tier=entity.requirements.min_solved_problem_tier.value,
            recommendation_period=entity.recommendation_period,
            active_yn=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
