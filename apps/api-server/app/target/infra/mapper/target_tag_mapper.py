"""TargetTag Mapper"""
from app.common.domain.vo.identifiers import TagId, TargetId
from app.target.domain.entity.target_tag import TargetTag
from app.target.infra.model.target_tag import TargetTagModel


class TargetTagMapper:
    """TargetTag Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: TargetTagModel) -> TargetTag:
        """Model -> Entity"""
        return TargetTag(
            target_tag_id=model.target_tag_id,
            tag_id=TagId(model.tag_id),
            target_id=TargetId(model.target_id),
            active=model.active_yn,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: TargetTag) -> TargetTagModel:
        """Entity -> Model"""
        return TargetTagModel(
            target_tag_id=entity.target_tag_id,
            tag_id=entity.tag_id.value,
            target_id=entity.target_id.value,
            active_yn=entity.active,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
