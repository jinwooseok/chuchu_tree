"""TagCustomization Mapper"""
from app.activity.domain.entity.tag_customization import TagCustomization
from app.activity.infra.model.tag_custom import TagCustomModel
from app.common.domain.enums import ExcludedReason
from app.common.domain.vo.identifiers import TagId, UserAccountId


class TagCustomizationMapper:
    """TagCustomization Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: TagCustomModel) -> TagCustomization:
        """Model -> Entity"""
        return TagCustomization(
            tag_custom_id=model.tag_custom_id,
            user_account_id=UserAccountId(model.user_account_id),
            tag_id=TagId(model.tag_id),
            excluded=model.excluded_yn,
            reason=ExcludedReason(model.excluded_reason) if model.excluded_reason else None,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(entity: TagCustomization) -> TagCustomModel:
        """Entity -> Model"""
        return TagCustomModel(
            tag_custom_id=entity.tag_custom_id,
            user_account_id=entity.user_account_id.value,
            tag_id=entity.tag_id.value,
            excluded_yn=entity.excluded,
            excluded_reason=entity.reason.value if entity.reason else None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )
