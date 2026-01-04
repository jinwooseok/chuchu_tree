"""Streak 엔티티와 Model 간 변환 매퍼"""

from app.baekjoon.domain.entity.streak import Streak
from app.baekjoon.infra.model.streak import StreakModel
from app.common.domain.vo.identifiers import BaekjoonAccountId, StreakId


class StreakMapper:
    """Streak 엔티티와 Model 간 변환을 담당하는 매퍼"""

    @staticmethod
    def to_model(entity: Streak) -> StreakModel:
        """도메인 엔티티를 SQLAlchemy 모델로 변환"""
        model = StreakModel()

        # ID (자동 생성)
        if entity.streak_id is not None:
            model.streak_id = entity.streak_id.value

        # 외래 키
        model.bj_account_id = entity.bj_account_id.value

        # 스트릭 정보
        model.streak_date = entity.streak_date
        model.solved_count = entity.solved_count

        # 메타데이터
        model.created_at = entity.created_at

        return model

    @staticmethod
    def to_entity(model: StreakModel) -> Streak:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return Streak(
            streak_id=StreakId(model.streak_id) if model.streak_id else None,
            bj_account_id=BaekjoonAccountId(model.bj_account_id),
            streak_date=model.streak_date,
            solved_count=model.solved_count,
            created_at=model.created_at
        )
