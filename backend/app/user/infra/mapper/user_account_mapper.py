from app.common.domain.vo.identifiers import UserAccountId
from app.user.domain.entity.user_account import UserAccount
from app.user.infra.mapper.account_link_mapper import AccountLinkMapper
from app.user.infra.mapper.user_target_mapper import UserTargetMapper
from app.user.infra.model.user_account import UserAccountModel


class UserAccountMapper:
    """Member 엔티티와 Model 간 변환을 담당하는 매퍼"""
    
    @staticmethod
    def to_model(entity: UserAccount) -> UserAccountModel:
        model = UserAccountModel()
        
        if entity.user_account_id is not None:
            model.user_account_id = entity.user_account_id.value
        
        model.provider = entity.provider
        model.provider_id = entity.provider_id
        model.profile_image = entity.profile_image
        model.registered_at = entity.registered_at
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at

        # 핵심: 자식 엔티티들도 모델로 변환하여 할당
        model.account_links = [
            AccountLinkMapper.to_model(link) for link in entity.account_links
        ]
        model.targets = [
            UserTargetMapper.to_model(target) for target in entity.targets
        ]
        
        return model
    
    @staticmethod
    def to_entity(model: UserAccountModel) -> UserAccount:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return UserAccount(
            user_account_id=UserAccountId(model.user_account_id),
            provider=model.provider,
            provider_id=model.provider_id,
            profile_image=model.profile_image,
            registered_at=model.registered_at,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            account_links=[
                AccountLinkMapper.to_entity(link) for link in model.account_links
            ],
            targets=[
                UserTargetMapper.to_entity(target) for target in model.targets
            ]
        )