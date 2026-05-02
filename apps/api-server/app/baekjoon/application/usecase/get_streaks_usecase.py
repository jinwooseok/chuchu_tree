"""스트릭 조회 Usecase (user_date_record 기반)"""

import logging

from app.activity.domain.repository.user_date_record_repository import UserDateRecordRepository
from app.baekjoon.application.command.get_streaks_command import GetStreaksCommand
from app.baekjoon.application.query.streaks_query import StreakItemQuery, StreaksQuery
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)


class GetStreaksUsecase:
    """스트릭 조회 Usecase (user_date_record 기반)"""

    def __init__(
        self,
        user_date_record_repository: UserDateRecordRepository,
        baekjoon_account_repository: BaekjoonAccountRepository
    ):
        self.user_date_record_repository = user_date_record_repository
        self.baekjoon_account_repository = baekjoon_account_repository

    @transactional(readonly=True)
    async def execute(self, command: GetStreaksCommand) -> StreaksQuery:
        """
        user_date_record 기반 날짜별 풀이 수 조회

        Args:
            command: 스트릭 조회 명령

        Returns:
            StreaksQuery: 날짜별 풀이 수 목록
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 1. UserAccount ID로 BaekjoonAccount 조회 (계정 존재 여부 확인)
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)

        if not bj_account:
            logger.error(f"[GetStreaksUsecase] 백준 계정을 찾을 수 없음: user_account_id={command.user_account_id}")
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 2. 날짜 범위로 user_date_record 조회
        date_records = await self.user_date_record_repository.find_by_user_and_date_range(
            user_account_id=user_account_id,
            bj_account_id=bj_account.bj_account_id.value,
            start_date=command.start_date,
            end_date=command.end_date
        )

        # 3. Query 객체로 변환 (streak_date = marked_date 매핑)
        streak_items = [
            StreakItemQuery(
                streak_date=udr.marked_date,
                solved_count=udr.solved_count
            )
            for udr in date_records
        ]

        return StreaksQuery(
            bj_account_id=bj_account.bj_account_id.value,
            streaks=streak_items,
            total_count=len(streak_items)
        )
