"""BaekjoonAccount 엔티티와 Model 간 변환 매퍼"""

from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.infra.model.bj_account import BjAccountModel
from app.common.domain.vo.identifiers import BaekjoonAccountId, TierId
from app.common.domain.vo.primitives import Rating, Statistics


class BaekjoonAccountMapper:
    """BaekjoonAccount 엔티티와 Model 간 변환을 담당하는 매퍼"""

    @staticmethod
    def to_model(entity: BaekjoonAccount) -> BjAccountModel:
        """도메인 엔티티를 SQLAlchemy 모델로 변환"""
        model = BjAccountModel()

        # ID
        model.bj_account_id = entity.bj_account_id.value

        # 백준 계정 정보
        model.tier_start_date = entity.tier_start_date
        model.tier_id = entity.current_tier_id.value
        model.rating = entity.rating.value
        model.contribution_count = entity.statistics.contribution_count
        model.class_ = entity.statistics.class_level
        model.longest_streak = entity.statistics.longest_streak

        # 메타데이터
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at

        return model

    @staticmethod
    def to_entity(model: BjAccountModel) -> BaekjoonAccount:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return BaekjoonAccount(
            bj_account_id=BaekjoonAccountId(model.bj_account_id),
            tier_start_date=model.tier_start_date,
            current_tier_id=TierId(model.tier_id),
            rating=Rating(model.rating),
            statistics=Statistics(
                model.contribution_count,
                model.class_,
                model.longest_streak
            ),
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            tier_histories=[],
            tag_skill_histories=[],
            problem_histories=[]
        )
