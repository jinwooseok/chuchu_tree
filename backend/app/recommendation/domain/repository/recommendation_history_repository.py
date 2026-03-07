from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.recommendation.domain.entity.recommendation_history import RecommendationHistory


class RecommendationHistoryRepository(ABC):

    @abstractmethod
    async def save(self, history: RecommendationHistory) -> RecommendationHistory:
        pass

    @abstractmethod
    async def find_by_user_account_id(
        self, user_account_id: UserAccountId
    ) -> list[RecommendationHistory]:
        """개인 추천 히스토리 조회 (study_id IS NULL)"""
        pass

    @abstractmethod
    async def find_by_study_id(
        self, study_id: StudyId, user_account_id: UserAccountId | None = None
    ) -> list[RecommendationHistory]:
        """스터디 추천 히스토리 조회 (user_account_id 미설정 시 스터디 전체)"""
        pass

    @abstractmethod
    async def delete_by_user_account_id(self, user_account_id: UserAccountId) -> None:
        """회원 탈퇴 시 해당 유저의 추천 히스토리 전체 삭제"""
        pass
