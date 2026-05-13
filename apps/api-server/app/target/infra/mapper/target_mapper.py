"""Target Mapper"""
from app.common.domain.vo.identifiers import TagId, TargetId
from app.target.domain.entity.target import Target
from app.target.domain.entity.target_tag import TargetTag
from app.target.infra.model.target import TargetModel


class TargetMapper:
    """Target Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: TargetModel, required_tags: list[TargetTag] = None) -> Target:
        """Model -> Entity"""
        return Target(
            target_id=TargetId(model.target_id),
            code=model.target_code,
            display_name=model.target_display_name,
            active=model.active_yn,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            required_tags=required_tags or []
        )

    @staticmethod
    def to_model(entity: Target) -> TargetModel:
        """Entity -> Model"""
        return TargetModel(
            target_id=entity.target_id.value if entity.target_id else None,
            target_code=entity.code,
            target_display_name=entity.display_name,
            active_yn=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
