from datetime import datetime
from app.activity.domain.entity.user_date_record import UserDateRecord
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.activity.domain.repository.user_date_record_repository import UserDateRecordRepository
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.event.link_bj_account_payload import LinkBjAccountPayload
from app.baekjoon.domain.gateway.solvedac_gateway import SolvedacGateway
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemId, TierId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class LinkBjAccountUsecase:
    """
    백준 계정과 연동하는 시나리오

    1. 백준 id와 유저 계정 id를 입력 받음
    2. 백준 id가 DB에 있다면 바로 연동 후 종료. 없다면 solvedAC API로 백준 계정 히스토리를 받음
    3. 백준 계정 테이블 저장
    4. 문제 히스토리 저장 (streak_id 없이)
    5. solved.ac history → user_date_record 생성
    6. 전체 문제 → user_problem_status 생성 (solved_yn=True, 날짜 미매핑)
    """

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        solvedac_gateway: SolvedacGateway,
        domain_event_bus: DomainEventBus,
        user_date_record_repository: UserDateRecordRepository,
        user_activity_repository: UserActivityRepository
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.solvedac_gateway = solvedac_gateway
        self.domain_event_bus = domain_event_bus
        self.user_date_record_repository = user_date_record_repository
        self.user_activity_repository = user_activity_repository

    @transactional
    async def execute(
        self,
        command: LinkBjAccountCommand
    ) -> None:
        bj_account_id = BaekjoonAccountId(command.bj_account_id)
        user_account_id = UserAccountId(command.user_account_id)

        existing_account = await self.baekjoon_account_repository.find_by_id(bj_account_id)

        event = DomainEvent(
            event_type="LINK_BAEKJOON_ACCOUNT_REQUESTED",
            data=LinkBjAccountPayload(
                user_account_id=command.user_account_id,
                bj_account_id=command.bj_account_id
            ),
            result_type=bool
        )

        if existing_account:
            # 기존 bj_account에 새 유저가 연동하는 경우
            # 다른 유저의 user_date_record를 재사용하지 않음:
            #   - 수동 문제 등록(주관적 날짜 배정)
            #   - 00:00~06:00 시간대 전날 조정 로직
            #   - 스케줄러 오류/재시도 로직
            #   위 요인들로 인해 다른 유저의 데이터가 오염되어 있을 수 있음
            # → solved.ac에서 히스토리를 새로 fetch하여 이 유저만의 데이터 생성
            user_data = await self.solvedac_gateway.fetch_user_data_first(command.bj_account_id)

            if user_data is None:
                raise APIException(ErrorCode.BAEKJOON_USER_NOT_FOUND)

            # 이 유저의 user_date_record 생성 (solved.ac 히스토리 기반, 새로 fetch)
            await self._create_user_date_records_from_history(
                user_account_id=user_account_id,
                bj_account_id=command.bj_account_id,
                history=user_data.history
            )

            # 이 유저의 user_problem_status 생성 (user_data.problems 기반)
            # BaekjoonAccountMapper.to_entity()는 problem_histories=[]를 반환하므로
            # 이미 fetch한 user_data.problems를 사용
            problem_ids = [p.problem_id for p in user_data.problems]
            await self._create_user_problem_statuses(
                user_account_id=user_account_id,
                bj_account_id=command.bj_account_id,
                problem_ids=problem_ids
            )

            event.data.problem_count = len(user_data.problems)
            await self.domain_event_bus.publish(event)
            return

        # 2-2. 존재하지 않으면 solved.ac에서 데이터 수집
        user_data = await self.solvedac_gateway.fetch_user_data_first(command.bj_account_id)

        if user_data is None:
            raise APIException(ErrorCode.BAEKJOON_USER_NOT_FOUND)

        # 3. BaekjoonAccount 엔티티 생성
        baekjoon_account = BaekjoonAccount.create(
            bj_account_id=bj_account_id,
            tier_id=TierId(user_data.user_info.tier)
        )

        baekjoon_account.update_rating(user_data.user_info.rating)
        baekjoon_account.update_statistics(
            contribution_count=0,
            class_level=user_data.user_info.class_level,
            longest_streak=user_data.user_info.max_streak
        )

        # 4. 문제 히스토리 기록 (streak_id 없이)
        for problem in user_data.problems:
            baekjoon_account.record_problem_solved(
                problem_id=ProblemId(problem.problem_id)
            )

        # 5. 저장
        await self.baekjoon_account_repository.save(baekjoon_account)

        # 6. solved.ac history → user_date_record 생성
        await self._create_user_date_records_from_history(
            user_account_id=user_account_id,
            bj_account_id=command.bj_account_id,
            history=user_data.history
        )

        # 7. 전체 문제 → user_problem_status 생성 (solved_yn=True, 날짜 미매핑)
        await self._create_user_problem_statuses(
            user_account_id=user_account_id,
            bj_account_id=command.bj_account_id,
            problem_ids=[p.problem_id for p in user_data.problems]
        )

        event.data.problem_count = len(user_data.problems)
        await self.domain_event_bus.publish(event)

    async def _create_user_date_records_from_history(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        history: list
    ) -> None:
        """solved.ac 누적 히스토리 → user_date_record (일별 풀이 수) 생성

        solved.ac history API는 문제 1개 풀 때마다 1건씩 기록하므로
        하루에 여러 건이 있을 수 있음 (예: 5문제 → 5건).
        날짜별 MAX(solved_count)를 구한 뒤 이전 날짜 MAX와의 delta로 일별 풀이 수를 계산.
        """
        if not history:
            return

        # 1단계: 날짜별 MAX(solved_count) 집계
        date_max: dict = {}
        for item in history:
            try:
                marked_date = datetime.fromisoformat(
                    item.timestamp.replace('Z', '+00:00')
                ).date()
                if marked_date not in date_max or item.solved_count > date_max[marked_date]:
                    date_max[marked_date] = item.solved_count
            except Exception:
                continue

        if not date_max:
            return

        # 2단계: 날짜 순 delta 계산 → user_date_record 생성
        records = []
        prev_max = 0
        for marked_date in sorted(date_max):
            day_max = date_max[marked_date]
            daily_count = max(0, day_max - prev_max)
            prev_max = day_max  # 누적값이므로 daily_count=0이어도 갱신

            if daily_count > 0:
                records.append(UserDateRecord.create(
                    user_account_id=user_account_id,
                    bj_account_id=bj_account_id,
                    marked_date=marked_date,
                    solved_count=daily_count
                ))

        if records:
            await self.user_date_record_repository.save_all(records)

    async def _create_user_problem_statuses(
        self,
        user_account_id: UserAccountId,
        bj_account_id: str,
        problem_ids: list[int]
    ) -> None:
        """solved_yn=True로 user_problem_status 생성 (날짜 미매핑)"""
        if not problem_ids:
            return

        statuses = []
        for problem_id in problem_ids:
            status = UserProblemStatus(
                user_problem_status_id=None,
                user_account_id=user_account_id,
                problem_id=ProblemId(problem_id),
                banned_yn=False,
                solved_yn=True,
                representative_tag_id=None,
                memo_title=None,
                content=None,
                date_records=[],  # 날짜 미매핑
                bj_account_id=bj_account_id,
            )
            statuses.append(status)

        await self.user_activity_repository.save_all_problem_records(statuses)
