import logging
from datetime import datetime, date

from app.activity.domain.entity.problem_date_record import ProblemDateRecord, RecordType
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.activity.domain.repository.user_date_record_repository import UserDateRecordRepository
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.entity.problem_history import ProblemHistory
from app.baekjoon.domain.gateway.solvedac_gateway import SolvedacGateway
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.common.domain.entity.system_log import SystemLog
from app.common.domain.entity.system_log_data import RefreshLogData, SchedulerLogData
from app.problem.application.service.problem_update_service import ProblemUpdateService
from app.common.domain.enums import SystemLogType, SystemLogStatus
from app.common.domain.repository.system_log_repository import SystemLogRepository
from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemId, TierId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.user.infra.model.account_link import AccountLinkModel
from sqlalchemy import select, and_

logger = logging.getLogger(__name__)


class UpdateBjAccountUsecase:
    """
    백준 계정 업데이트 시나리오

    1. 유저 id로 백준 id를 찾음
    2. 그 백준 id를 기준으로 업데이트 진행
    3. 신규 문제 → user_problem_status 생성 (solved_yn=True, 날짜 미매핑)
    4. 오늘 날짜 user_date_record 생성/업데이트
    5. system_log에 SUCCESS/FAILED 기록 (SCHEDULER 또는 REFRESH 타입)
    """

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        problem_history_repository: ProblemHistoryRepository,
        solvedac_gateway: SolvedacGateway,
        user_date_record_repository: UserDateRecordRepository,
        user_activity_repository: UserActivityRepository,
        system_log_repository: SystemLogRepository,
        problem_update_service: ProblemUpdateService,
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.solvedac_gateway = solvedac_gateway
        self.problem_history_repository = problem_history_repository
        self.user_date_record_repository = user_date_record_repository
        self.user_activity_repository = user_activity_repository
        self.system_log_repository = system_log_repository
        self.problem_update_service = problem_update_service

    @transactional
    async def execute(self, user_account_id: int) -> None:
        existing_account = await self.baekjoon_account_repository.find_by_user_id(UserAccountId(user_account_id))

        if existing_account is None:
            raise APIException(ErrorCode.UNLINKED_USER)

        await self._sync_solved_ac(
            existing_account,
            restrict_to_user_id=user_account_id,
            log_type=SystemLogType.REFRESH,
        )

    @transactional
    async def execute_bulk(self) -> None:
        bj_accounts: list[BaekjoonAccount] = await self.baekjoon_account_repository.find_all()
        for bj_account in bj_accounts:
            try:
                await self._sync_solved_ac(bj_account, log_type=SystemLogType.SCHEDULER)
            except Exception as e:
                logger.error(f"[UpdateBjAccountUsecase] 계정 업데이트 실패: {bj_account.bj_account_id.value}, error={e}")

    async def _sync_solved_ac(
        self,
        bj_account: BaekjoonAccount,
        log_type: SystemLogType,
        restrict_to_user_id: int | None = None,
    ):
        today = date.today()

        try:
            existing_problem_history_ids = await self.problem_history_repository.find_solved_ids_by_bj_account_id(
                bj_account.bj_account_id
            )

            # solved.ac 데이터 수집
            user_data = await self.solvedac_gateway.fetch_user_data_first(bj_account.bj_account_id.value)

            if user_data is None:
                raise APIException(ErrorCode.BAEKJOON_USER_NOT_FOUND)

            # 유저 기본 정보 업데이트
            bj_account.update_tier(TierId(user_data.user_info.tier))
            bj_account.update_rating(user_data.user_info.rating)
            bj_account.update_statistics(
                contribution_count=0,
                class_level=user_data.user_info.class_level,
                longest_streak=user_data.user_info.max_streak
            )

            # 신규 문제 필터링
            new_problems = [p for p in user_data.problems if p.problem_id not in existing_problem_history_ids]

            # 신규 problem_history 저장 (streak_id 없이)
            if new_problems:
                # problem 테이블 보장 먼저 (FK 제약: problem_history.problem_id → problem.problem_id)
                new_problem_ids = [p.problem_id for p in new_problems]
                valid_problem_ids_list = await self.problem_update_service.ensure_problems_exist(new_problem_ids)
                valid_id_set = set(valid_problem_ids_list)

                new_history_entities = [
                    ProblemHistory.create(
                        bj_account_id=bj_account.bj_account_id,
                        problem_id=ProblemId(p.problem_id)
                    )
                    for p in new_problems
                    if p.problem_id in valid_id_set
                ]
                await self.problem_history_repository.save_all(new_history_entities)

                # valid_id_set 기준으로 new_problems 필터링 (이후 added_problem_ids 계산에 반영)
                new_problems = [p for p in new_problems if p.problem_id in valid_id_set]

            # bj_account 통계 업데이트
            await self.baekjoon_account_repository.update_stat(bj_account)

            # 연결된 user_account 처리 (restrict_to_user_id 지정 시 해당 유저만)
            linked_user_ids = await self._find_linked_user_account_ids(bj_account.bj_account_id)
            if restrict_to_user_id is not None:
                linked_user_ids = [uid for uid in linked_user_ids if uid == restrict_to_user_id]

            added_problem_ids = [p.problem_id for p in new_problems]

            for user_account_id in linked_user_ids:
                ua_id = UserAccountId(user_account_id)

                # a. 신규 user_problem_status 생성 (solved_yn=True, 스케줄러 실행일로 날짜 매핑)
                if new_problems:
                    statuses = [
                        UserProblemStatus(
                            user_problem_status_id=None,
                            user_account_id=ua_id,
                            problem_id=ProblemId(p.problem_id),
                            banned_yn=False,
                            solved_yn=True,
                            representative_tag_id=None,
                            memo_title=None,
                            content=None,
                            date_records=[
                                ProblemDateRecord.create(
                                    user_problem_status_id=None,
                                    marked_date=today,
                                    record_type=RecordType.SOLVED,
                                )
                            ],
                            bj_account_id=bj_account.bj_account_id.value,
                        )
                        for p in new_problems
                    ]
                    await self.user_activity_repository.save_all_problem_records(statuses)

                # b. 오늘 날짜 user_date_record 생성/업데이트 (solved_count += 신규 건수)
                if new_problems:
                    await self.user_date_record_repository.upsert_increment(
                        user_account_id=ua_id,
                        bj_account_id=bj_account.bj_account_id.value,
                        target_date=today,
                        increment=len(new_problems)
                    )

            # system_log에 SUCCESS 기록
            log = self._build_success_log(
                log_type=log_type,
                bj_account_id=bj_account.bj_account_id,
                run_date=today,
                added_problem_ids=added_problem_ids,
                new_solved_count=len(new_problems),
                affected_user_ids=linked_user_ids,
                restrict_to_user_id=restrict_to_user_id,
            )
            await self.system_log_repository.save(log)

        except Exception as e:
            # system_log에 FAILED 기록
            try:
                log = self._build_failed_log(
                    log_type=log_type,
                    bj_account_id=bj_account.bj_account_id,
                    run_date=today,
                    error=str(e),
                    restrict_to_user_id=restrict_to_user_id,
                )
                await self.system_log_repository.save(log)
            except Exception as log_err:
                logger.error(f"[UpdateBjAccountUsecase] system_log 저장 실패: {log_err}")
            raise

    def _build_success_log(
        self,
        log_type: SystemLogType,
        bj_account_id: BaekjoonAccountId,
        run_date: date,
        added_problem_ids: list[int],
        new_solved_count: int,
        affected_user_ids: list[int],
        restrict_to_user_id: int | None,
    ) -> SystemLog:
        if log_type == SystemLogType.REFRESH:
            log_data = RefreshLogData(
                bj_account_id=bj_account_id.value,
                requesting_user_account_id=restrict_to_user_id or 0,
                run_date=run_date.isoformat(),
                added_problem_ids=added_problem_ids,
                new_solved_count=new_solved_count,
                affected_user_ids=affected_user_ids,
                error=None,
            ).to_dict()
        else:
            log_data = SchedulerLogData(
                bj_account_id=bj_account_id.value,
                run_date=run_date.isoformat(),
                added_problem_ids=added_problem_ids,
                new_solved_count=new_solved_count,
                affected_user_ids=affected_user_ids,
                error=None,
            ).to_dict()

        return SystemLog.create(
            log_type=log_type,
            status=SystemLogStatus.SUCCESS,
            log_data=log_data,
            should_notify=False,
        )

    def _build_failed_log(
        self,
        log_type: SystemLogType,
        bj_account_id: BaekjoonAccountId,
        run_date: date,
        error: str,
        restrict_to_user_id: int | None,
    ) -> SystemLog:
        if log_type == SystemLogType.REFRESH:
            log_data = RefreshLogData(
                bj_account_id=bj_account_id.value,
                requesting_user_account_id=restrict_to_user_id or 0,
                run_date=run_date.isoformat(),
                added_problem_ids=[],
                new_solved_count=0,
                affected_user_ids=[],
                error=error,
            ).to_dict()
        else:
            log_data = SchedulerLogData(
                bj_account_id=bj_account_id.value,
                run_date=run_date.isoformat(),
                added_problem_ids=[],
                new_solved_count=0,
                affected_user_ids=[],
                error=error,
            ).to_dict()

        return SystemLog.create(
            log_type=log_type,
            status=SystemLogStatus.FAILED,
            log_data=log_data,
            should_notify=True,
        )

    async def _find_linked_user_account_ids(
        self,
        bj_account_id: BaekjoonAccountId
    ) -> list[int]:
        """특정 bj_account에 연결된 모든 user_account_id 조회"""
        session = self.baekjoon_account_repository.session
        stmt = select(AccountLinkModel.user_account_id).where(
            and_(
                AccountLinkModel.bj_account_id == bj_account_id.value,
                AccountLinkModel.deleted_at.is_(None)
            )
        )
        result = await session.execute(stmt)
        return list(result.scalars().all())
