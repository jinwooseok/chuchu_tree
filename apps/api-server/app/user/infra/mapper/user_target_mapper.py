from app.common.domain.vo.identifiers import UserAccountId, TargetId
from app.user.domain.entity.user_target import UserTarget
from app.user.infra.model.user_target import UserTargetModel


class UserTargetMapper:
    """UserTarget 엔티티와 Model 간 변환을 담당하는 매퍼"""
    
    @staticmethod
    def to_model(entity: UserTarget) -> UserTargetModel:
        """도메인 엔티티를 SQLAlchemy 모델로 변환"""
        
        model = UserTargetModel()
        
        # ID
        if entity.user_target_id is not None:
            model.user_target_id = entity.user_target_id
        
        # Foreign Keys
        model.user_account_id = entity.user_account_id.value
        model.target_id = entity.target_id.value
        
        # 메타데이터
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        
        return model
    
    @staticmethod
    def to_entity(model: UserTargetModel) -> UserTarget:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return UserTarget(
            user_target_id=model.user_target_id,
            user_account_id=UserAccountId(model.user_account_id),
            target_id=TargetId(model.target_id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
