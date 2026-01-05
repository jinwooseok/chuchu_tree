"""백준 내 정보 조회 Usecase"""

import logging
from datetime import date, timedelta

from app.baekjoon.application.command.get_baekjoon_me_command import GetBaekjoonMeCommand
from app.baekjoon.application.query.baekjoon_account_info_query import (
    BjAccountStatQuery,
    BjAccountQuery,
    UserAccountQuery,
    BaekjoonMeQuery
)
from app.baekjoon.application.query.streaks_query import StreakItemQuery
from app.baekjoon.domain.event.get_user_account_info_payload import GetUserAccountInfoPayload
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.streak_repository import StreakRepository
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import UserAccountId, TierId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.tier.domain.repository.tier_repository import TierRepository
from app.user.application.query.user_account_info_query import GetUserAccountInfoQuery

logger = logging.getLogger(__name__)


class GetBaekjoonMeUsecase:
    """백준 내 정보 조회 Usecase"""

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        streak_repository: StreakRepository,
        tier_repository: TierRepository,
        domain_event_bus: DomainEventBus
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.streak_repository = streak_repository
        self.tier_repository = tier_repository
        self.domain_event_bus = domain_event_bus

    @transactional
    async def execute(self, command: GetBaekjoonMeCommand) -> BaekjoonMeQuery:
        """
        백준 내 정보 조회

        Args:
            command: 백준 내 정보 조회 명령

        Returns:
            BaekjoonMeQuery: 백준 내 정보 (유저 계정 + 백준 계정 + 스트릭)
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 1. 이벤트 발행하여 UserAccount 정보 조회
        event = DomainEvent(
            event_type="GET_USER_ACCOUNT_INFO_REQUESTED",
            data=GetUserAccountInfoPayload(user_account_id=command.user_account_id),
            result_type=GetUserAccountInfoQuery
        )

        user_account_info = await self.domain_event_bus.publish(event)

        if not user_account_info:
            logger.error(f"[GetBaekjoonMeUsecase] 유저 계정을 찾을 수 없음: {command.user_account_id}")
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 2. BaekjoonAccount 정보와 연동 일자 조회
        account_with_link = await self.baekjoon_account_repository.find_by_user_id_with_link_date(
            user_account_id
        )

        if not account_with_link:
            logger.error(f"[GetBaekjoonMeUsecase] 백준 계정 연동 정보를 찾을 수 없음: {command.user_account_id}")
            raise APIException(ErrorCode.UNLINKED_USER)

        bj_account, linked_at = account_with_link

        # 3. Tier 정보 조회
        tier = await self.tier_repository.find_by_id(bj_account.current_tier_id)
        tier_name = tier.tier_code

        # 4. 최근 365일 스트릭 조회
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        streaks = await self.streak_repository.find_by_account_and_date_range(
            bj_account_id=bj_account.bj_account_id,
            start_date=start_date,
            end_date=end_date
        )

        # 5. Query 객체로 변환
        user_account_query = UserAccountQuery(
            user_account_id=user_account_info.user_account_id,
            profile_image_url=user_account_info.profile_image,
            registered_at=user_account_info.registered_at
        )

        stat_query = BjAccountStatQuery(
            tier_id=bj_account.current_tier_id.value,
            tier_name=tier_name,
            longest_streak=bj_account.statistics.longest_streak,
            rating=bj_account.rating.value,
            class_level=bj_account.statistics.class_level,
            tier_start_date=bj_account.tier_start_date
        )

        streak_queries = [
            StreakItemQuery(
                streak_date=streak.streak_date,
                solved_count=streak.solved_count
            )
            for streak in streaks
        ]

        bj_account_query = BjAccountQuery(
            bj_account_id=bj_account.bj_account_id.value,
            stat=stat_query,
            streaks=streak_queries,
            registered_at=bj_account.created_at
        )

        return BaekjoonMeQuery(
            user_account=user_account_query,
            bj_account=bj_account_query,
            linked_at=linked_at
        )
