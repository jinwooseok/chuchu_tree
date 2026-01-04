"""solved.ac API 데이터 수집을 위한 Gateway 인터페이스"""

from abc import ABC, abstractmethod

from app.baekjoon.domain.vo.solvedac_data import SolvedacUserDataVO


class SolvedacGateway(ABC):
    """solved.ac API 데이터 수집 Gateway 인터페이스"""

    @abstractmethod
    async def fetch_user_data(self, bj_user_id: str) -> SolvedacUserDataVO | None:
        """
        백준 유저 ID로 solved.ac에서 유저 데이터 수집

        Args:
            bj_user_id: 백준 유저 ID (닉네임)

        Returns:
            SolvedacUserDataVO: 유저의 모든 푼 문제 및 히스토리 데이터
            None: 존재하지 않는 유저이거나 데이터 수집 실패

        Raises:
            APIException: API 요청 실패 또는 제한 초과
        """
        pass
