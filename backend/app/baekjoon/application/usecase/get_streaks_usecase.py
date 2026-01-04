"""스트릭 조회 Usecase"""

import logging

from app.baekjoon.application.command.get_streaks_command import GetStreaksCommand
from app.baekjoon.application.query.streaks_query import StreakItemQuery, StreaksQuery
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.streak_repository import StreakRepository
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)


class GetStreaksUsecase:
    """스트릭 조회 Usecase"""

    def __init__(
        self,
        streak_repository: StreakRepository,
        baekjoon_account_repository: BaekjoonAccountRepository
    ):
        self.streak_repository = streak_repository
        self.baekjoon_account_repository = baekjoon_account_repository

    @transactional
    async def execute(self, command: GetStreaksCommand) -> StreaksQuery:
        """
        스트릭 조회

        Args:
            command: 스트릭 조회 명령

        Returns:
            StreaksQuery: 스트릭 목록
        """
        # 1. UserAccount ID로 BaekjoonAccount 조회
        user_account_id = UserAccountId(command.user_account_id)
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)

        if not bj_account:
            logger.error(f"[GetStreaksUsecase] 백준 계정을 찾을 수 없음: user_account_id={command.user_account_id}")
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 2. 날짜 범위로 스트릭 조회
        streaks = await self.streak_repository.find_by_account_and_date_range(
            bj_account_id=bj_account.bj_account_id,
            start_date=command.start_date,
            end_date=command.end_date
        )

        # 3. Query 객체로 변환
        streak_items = [
            StreakItemQuery(
                streak_date=streak.streak_date,
                solved_count=streak.solved_count
            )
            for streak in streaks
        ]

        return StreaksQuery(
            bj_account_id=bj_account.bj_account_id.value,
            streaks=streak_items,
            total_count=len(streak_items)
        )
