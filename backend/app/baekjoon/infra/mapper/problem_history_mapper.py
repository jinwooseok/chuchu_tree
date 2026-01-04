"""ProblemHistory 엔티티와 Model 간 변환 매퍼"""

from app.baekjoon.domain.entity.problem_history import ProblemHistory
from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemId, ProblemHistoryId, StreakId


class ProblemHistoryMapper:
    """ProblemHistory 엔티티와 Model 간 변환을 담당하는 매퍼"""

    @staticmethod
    def to_model(entity: ProblemHistory) -> ProblemHistoryModel:
        """도메인 엔티티를 SQLAlchemy 모델로 변환"""
        model = ProblemHistoryModel()

        # ID (자동 생성)
        if entity.problem_history_id is not None:
            model.problem_history_id = entity.problem_history_id.value

        # 외래 키
        model.bj_account_id = entity.bj_account_id.value
        model.problem_id = entity.problem_id.value

        # 스트릭 연동 (나중에 업데이트)
        if entity.streak_id is not None:
            model.streak_id = entity.streak_id.value

        # 메타데이터
        model.created_at = entity.created_at

        return model

    @staticmethod
    def to_entity(model: ProblemHistoryModel) -> ProblemHistory:
        """SQLAlchemy 모델을 도메인 엔티티로 변환"""
        return ProblemHistory(
            problem_history_id=ProblemHistoryId(model.problem_history_id) if model.problem_history_id else None,
            bj_account_id=BaekjoonAccountId(model.bj_account_id),
            problem_id=ProblemId(model.problem_id),
            streak_id=StreakId(model.streak_id) if model.streak_id else None,
            created_at=model.created_at
        )
