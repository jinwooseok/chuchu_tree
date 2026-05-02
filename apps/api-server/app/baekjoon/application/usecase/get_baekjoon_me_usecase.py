"""백준 내 정보 조회 Usecase"""

import logging
from datetime import date, timedelta

from app.activity.domain.repository.user_date_record_repository import UserDateRecordRepository
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
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import UserAccountId, TierId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.query.study_query import MyStudyItemQuery
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.tier.domain.repository.tier_repository import TierRepository

logger = logging.getLogger(__name__)


class GetBaekjoonMeUsecase:
    """백준 내 정보 조회 Usecase"""

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        user_date_record_repository: UserDateRecordRepository,
        tier_repository: TierRepository,
        domain_event_bus: DomainEventBus,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.user_date_record_repository = user_date_record_repository
        self.tier_repository = tier_repository
        self.domain_event_bus = domain_event_bus
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository

    @transactional(readonly=True)
    async def execute(self, command: GetBaekjoonMeCommand) -> BaekjoonMeQuery:
        user_account_id = UserAccountId(command.user_account_id)

        # 1. 이벤트 발행하여 UserAccount 정보 조회
        event = DomainEvent(
            event_type="GET_USER_ACCOUNT_INFO_REQUESTED",
            data=GetUserAccountInfoPayload(user_account_id=command.user_account_id),
            result_type=UserAccountQuery
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

        # 4. 최근 365일 user_date_record 조회 (streak 대체)
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        date_records = await self.user_date_record_repository.find_by_user_and_date_range(
            user_account_id=user_account_id,
            bj_account_id=bj_account.bj_account_id.value,
            start_date=start_date,
            end_date=end_date
        )

        # 5. Query 객체로 변환
        user_account_query = UserAccountQuery(
            user_account_id=user_account_info.user_account_id,
            profile_image_url=user_account_info.profile_image_url,
            registered_at=user_account_info.registered_at,
            targets=user_account_info.targets,
            is_synced=user_account_info.is_synced,
            user_code=user_account_info.user_code,
        )

        stat_query = BjAccountStatQuery(
            tier_id=bj_account.current_tier_id.value,
            tier_name=tier_name,
            longest_streak=bj_account.statistics.longest_streak,
            rating=bj_account.rating.value,
            class_level=bj_account.statistics.class_level,
            tier_start_date=bj_account.tier_start_date
        )

        # user_date_record → StreakItemQuery (streak_date = marked_date)
        streak_queries = [
            StreakItemQuery(
                streak_date=udr.marked_date,
                solved_count=udr.solved_count
            )
            for udr in date_records
        ]

        bj_account_query = BjAccountQuery(
            bj_account_id=bj_account.bj_account_id.value,
            stat=stat_query,
            streaks=streak_queries,
            registered_at=bj_account.created_at
        )

        # 6. 참여 중인 스터디 목록 조회
        studies = await self.study_repository.find_by_member_user_account_id(user_account_id)
        owner_ids = list({s.owner_user_account_id.value for s in studies})
        owner_infos = await self.user_search_repository.find_by_user_account_ids(owner_ids)
        owner_map = {u.user_account_id: u for u in owner_infos}

        study_queries = [
            MyStudyItemQuery(
                study_id=s.study_id.value,
                study_name=s.study_name,
                owner_user_account_id=s.owner_user_account_id.value,
                owner_bj_account_id=owner_map[s.owner_user_account_id.value].bj_account_id
                if s.owner_user_account_id.value in owner_map else "",
                owner_user_code=owner_map[s.owner_user_account_id.value].user_code
                if s.owner_user_account_id.value in owner_map else "",
                description=s.description,
                max_members=s.max_members,
                member_count=s.active_member_count(),
                created_at=s.created_at.isoformat(),
            )
            for s in studies
        ]

        return BaekjoonMeQuery(
            user_account=user_account_query,
            bj_account=bj_account_query,
            linked_at=linked_at,
            studies=study_queries,
        )
