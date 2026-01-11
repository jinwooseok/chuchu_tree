"""Tag Mapper"""
from sqlalchemy import inspect
from app.common.domain.enums import ExcludedReason, TagLevel
from app.common.domain.vo.identifiers import TagId, TierId
from app.common.domain.vo.primitives import TierRange
from app.tag.domain.entity.tag import Tag
from app.tag.domain.entity.tag_relation import TagRelation
from app.tag.domain.vo.tag_exclusion import TagExclusion
from app.tag.infra.model.tag import TagModel
from app.tag.infra.model.tag_relation import TagRelationModel
from app.target.infra.mapper.target_mapper import TargetMapper


class TagRelationMapper:
    @staticmethod
    def to_entity(model: TagRelationModel) -> TagRelation:
        return TagRelation(
            tag_relation_id=model.tag_relation_id,
            leading_tag_id=TagId(model.leading_tag_id),
            sub_tag_id=TagId(model.sub_tag_id),
            active=model.active_yn,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(entity: TagRelation) -> TagRelationModel:
        return TagRelationModel(
            tag_relation_id=entity.tag_relation_id,
            leading_tag_id=entity.leading_tag_id.value,
            sub_tag_id=entity.sub_tag_id.value,
            active_yn=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )


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
        aliases: list[str] = []

        if model.aliases:
            if isinstance(model.aliases, list):
                aliases = [item for item in model.aliases]
        
        ins = inspect(model)

        # 1. parent_tag_relations 처리
        parent_tag_relations = []
        # 'unloaded' 목록에 없다는 것은 이미 DB에서 가져왔다는 뜻입니다.
        if "parent_tag_relations" not in ins.unloaded:
            if model.parent_tag_relations:
                parent_tag_relations = [
                    TagRelationMapper.to_entity(m) for m in model.parent_tag_relations
                ]

        # 2. targets 처리
        targets = []
        if "targets" not in ins.unloaded:
            if model.targets:
                targets = [TargetMapper.to_entity(m) for m in model.targets]
        
        return Tag(
            tag_id=TagId(model.tag_id) if model.tag_id else None,
            code=model.tag_code,
            tag_display_name=model.tag_display_name,
            level=TagLevel(model.tag_level),
            exclusion=exclusion,
            applicable_tier_range=tier_range,
            min_solved_person_count=model.min_solved_person_count,
            aliases=aliases,
            problem_count=model.tag_problem_count,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            parent_tag_relations=parent_tag_relations,
            targets=targets
        )

    @staticmethod
    def to_model(entity: Tag) -> TagModel:
        """Entity -> Model"""
        aliases_json = {f"alias_{i}": alias for i, alias in enumerate(entity.aliases)}

        model = TagModel(
            tag_id=entity.tag_id.value if entity.tag_id else None,
            tag_code=entity.code,
            tag_display_name=entity.tag_display_name,
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
        return model
