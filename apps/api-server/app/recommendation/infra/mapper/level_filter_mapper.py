"""LevelFilter Mapper"""

from app.common.domain.enums import FilterCode
from app.common.domain.vo.identifiers import LevelFilterId, TagSkillId
from app.recommendation.domain.entity.level_filter import LevelFilter
from app.recommendation.infra.model.problem_recommendation_level_filter import ProblemRecommendationLevelFilterModel


class LevelFilterMapper:
    """LevelFilter Entity와 Model 간 변환"""

    @staticmethod
    def to_entity(model: ProblemRecommendationLevelFilterModel | None) -> LevelFilter | None:
        """Model -> Entity"""
        if not model:
            return None

        return LevelFilter(
            filter_id=LevelFilterId(model.filter_id) if model.filter_id else None,
            filter_code=FilterCode(model.filter_code),
            display_name=model.display_name,
            max_user_tier_diff=model.max_user_tier_diff,
            min_user_tier_diff=model.min_user_tier_diff,
            tag_skill_code=model.tag_skill_code,
            min_tag_skill_rate=model.min_tag_skill_rate,
            max_tag_skill_rate=model.max_tag_skill_rate,
            active=model.active_yn,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: LevelFilter) -> ProblemRecommendationLevelFilterModel:
        """Entity -> Model"""
        return ProblemRecommendationLevelFilterModel(
            filter_id=entity.filter_id.value if entity.filter_id else None,
            filter_code=entity.filter_code.value,
            display_name=entity.display_name,
            max_user_tier_diff=entity.max_user_tier_diff,
            min_user_tier_diff=entity.min_user_tier_diff,
            tag_skill_code=entity.tag_skill_code,
            min_tag_skill_rate=entity.min_tag_skill_rate,
            max_tag_skill_rate=entity.max_tag_skill_rate,
            active_yn=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
