"""Tag Mapper"""
from app.common.domain.enums import ExcludedReason, TagLevel
from app.common.domain.vo.identifiers import TagId, TierId
from app.common.domain.vo.primitives import TierRange
from app.tag.domain.entity.tag import Tag
from app.tag.domain.vo.tag_exclusion import TagExclusion
from app.tag.infra.model.tag import TagModel


class TagMapper:
    """Tag Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: TagModel) -> Tag:
        """Model -> Entity"""
        # Exclusion 처리
        if model.excluded_yn and model.excluded_reason:
            exclusion = TagExclusion.is_excluded(ExcludedReason(model.excluded_reason))
        else:
            exclusion = TagExclusion.is_not_excluded()

        # TierRange 처리
        min_tier_id = TierId(model.min_problem_tier_id) if model.min_problem_tier_id else None
        max_tier_id = TierId(model.max_problem_tier_id) if model.max_problem_tier_id else None
        tier_range = TierRange(min_tier_id, max_tier_id)

        # Aliases 처리 (JSON -> list[str])
        aliases = model.aliases if model.aliases else []
        if isinstance(aliases, dict):
            aliases = list(aliases.values()) if aliases else []

        return Tag(
            tag_id=TagId(model.tag_id),
            code=model.tag_code,
            level=TagLevel(model.tag_level),
            exclusion=exclusion,
            applicable_tier_range=tier_range,
            min_solved_person_count=model.min_solved_person_count,
            aliases=aliases,
            problem_count=model.tag_problem_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            sub_tags=[]
        )

    @staticmethod
    def to_model(entity: Tag) -> TagModel:
        """Entity -> Model"""
        # Aliases 처리 (list[str] -> JSON)
        aliases_json = {f"alias_{i}": alias for i, alias in enumerate(entity.aliases)}

        return TagModel(
            tag_id=entity.tag_id.value if entity.tag_id else None,
            tag_code=entity.code,
            tag_display_name=entity.code,  # display_name이 있다면 사용
            tag_level=entity.level.value,
            excluded_yn=entity.exclusion.is_excluded,
            excluded_reason=entity.exclusion.reason.value if entity.exclusion.reason else None,
            min_problem_tier_id=entity.applicable_tier_range.min_tier_id.value if entity.applicable_tier_range.min_tier_id else None,
            max_problem_tier_id=entity.applicable_tier_range.max_tier_id.value if entity.applicable_tier_range.max_tier_id else None,
            min_solved_person_count=entity.min_solved_person_count,
            aliases=aliases_json,
            tag_problem_count=entity.problem_count,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
