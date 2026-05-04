"""AccountLink 엔티티와 Model 간 변환 매퍼"""

from app.common.domain.vo.identifiers import AccountLinkId, BaekjoonAccountId, UserAccountId
from app.user.domain.entity.account_link import AccountLink
from app.user.infra.model.account_link import AccountLinkModel


class AccountLinkMapper:
    """AccountLink 엔티티와 Model 간 변환을 담당하는 매퍼"""

    @staticmethod
    def to_model(entity: AccountLink) -> AccountLinkModel:
        """도메인 엔티티를 SQLAlchemy 모델로 변환"""
        model = AccountLinkModel()

        # ID
        if entity.account_link_id is not None:
            model.account_link_id = entity.account_link_id.value

        # 외래 키
        if entity.user_account_id is not None:
            model.user_account_id = entity.user_account_id.value
        model.bj_account_id = entity.bj_account_id.value

        # 메타데이터
        model.created_at = entity.created_at
        model.deleted_at = entity.deleted_at
        model.is_synced = entity.is_synced

        return model

    @staticmethod
    def to_entity(model: AccountLinkModel) -> AccountLink:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return AccountLink(
            account_link_id=AccountLinkId(model.account_link_id),
            user_account_id=UserAccountId(model.user_account_id),
            bj_account_id=BaekjoonAccountId(model.bj_account_id),
            created_at=model.created_at,
            deleted_at=model.deleted_at,
            is_synced=model.is_synced
        )
