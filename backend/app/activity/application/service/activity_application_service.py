"""Activity Application Service"""
import logging
from calendar import monthrange
from collections import defaultdict
from datetime import date, datetime, timedelta

from app.activity.application.command.ban_problem_command import BanProblemCommand
from app.activity.application.command.batch_create_solved_problems_command import BatchCreateSolvedProblemsCommand
from app.activity.application.command.delete_user_activity_command import DeleteUserActivityCommand
from app.activity.application.command.set_representative_tag_command import SetProblemRepresentativeTagCommand
from app.activity.application.command.tag_custom_command import TagCustomCommand
from app.activity.application.command.update_solved_problems_command import UpdateSolvedProblemsCommand
from app.activity.application.command.update_solved_will_solve_problems_command import UpdateSolvedAndWillSolveProblemsCommand
from app.activity.application.command.update_will_solve_problems import UpdateWillSolveProblemsCommand
from app.activity.application.query.banned_list_query import BannedProblemsQuery, BannedTagsQuery
from app.activity.application.query.monthly_activity_data_query import (
    DailyActivityQuery,
    MonthlyActivityDataQuery,
    ProblemActivityInfo
)
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.problem.application.query.problems_info_query import ProblemsInfoQuery
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.event.payloads import GetProblemsInfoPayload, GetTagSummaryPayload, GetTagSummaryResultPayload, GetTagSummarysPayload, GetTagSummarysResultPayload
from app.activity.domain.entity.user_date_record import UserDateRecord
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.activity.domain.repository.user_date_record_repository import UserDateRecordRepository
from app.baekjoon.domain.event.get_monthly_activity_data_payload import GetMonthlyActivityDataPayload
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.problem.application.service.problem_update_service import ProblemUpdateService
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.entity.system_log import SystemLog
from app.common.domain.entity.system_log_data import BulkUpdateLogData
from app.common.domain.enums import ExcludedReason, SystemLogType, SystemLogStatus
from app.common.domain.repository.system_log_repository import SystemLogRepository
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId
from app.user.application.command.mark_synced_command import MarkSyncedCommand
from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)

@event_register_handlers()
class ActivityApplicationService:
    """Activity Application Service"""

    def __init__(
        self,
        user_activity_repository: UserActivityRepository,
        domain_event_bus: DomainEventBus,
        baekjoon_account_repository: BaekjoonAccountRepository,
        problem_history_repository: ProblemHistoryRepository,
        user_date_record_repository: UserDateRecordRepository,
        problem_update_service: ProblemUpdateService | None = None,
        system_log_repository: SystemLogRepository | None = None,
    ):
        self.user_activity_repository = user_activity_repository
        self.domain_event_bus = domain_event_bus
        self.baekjoon_account_repository = baekjoon_account_repository
        self.problem_history_repository = problem_history_repository
        self.user_date_record_repository = user_date_record_repository
        self.problem_update_service = problem_update_service
        self.system_log_repository = system_log_repository

    @event_handler("GET_MONTHLY_ACTIVITY_DATA_REQUESTED")
    @transactional(readonly=True)
    async def get_monthly_activity_data(
        self,
        payload: GetMonthlyActivityDataPayload
    ) -> MonthlyActivityDataQuery:
        user_account_id = UserAccountId(payload.user_account_id)

        # 1. 월간 푼 문제 기록 조회
        problem_records = await self.user_activity_repository.find_monthly_problem_records(
            user_id=user_account_id,
            year=payload.year,
            month=payload.month
        )

        # 2. 월간 풀 예정 문제 조회
        will_solve_problems = await self.user_activity_repository.find_monthly_will_solve_problems(
            user_id=user_account_id,
            year=payload.year,
            month=payload.month
        )

        # 3. 날짜별로 그룹화 (SOLVED: 중복 제거, WILL_SOLVE: DB unique index로 보장)
        daily_map = defaultdict(lambda: {"solved": [], "will_solve": []})
        seen_solved = defaultdict(set)  # DB unique index 보장 전까지 런타임 중복 방지 유지
        seen_will_solve = defaultdict(set)

        for status in problem_records:
            if status.solved_yn:
                pid = status.problem_id.value
                if pid not in seen_solved[status.marked_date]:
                    seen_solved[status.marked_date].add(pid)
                    rep_tag_id = status.representative_tag_id.value if status.representative_tag_id else None
                    daily_map[status.marked_date]["solved"].append(
                        ProblemActivityInfo(problem_id=pid, representative_tag_id=rep_tag_id)
                    )

        for status in will_solve_problems:
            pid = status.problem_id.value
            # WILL_SOLVE는 같은 문제를 여러 날짜에 등록 가능
            key = (pid, status.marked_date)
            if key not in seen_will_solve[status.marked_date]:
                seen_will_solve[status.marked_date].add(key)
                rep_tag_id = status.representative_tag_id.value if status.representative_tag_id else None
                daily_map[status.marked_date]["will_solve"].append(
                    ProblemActivityInfo(problem_id=pid, representative_tag_id=rep_tag_id)
                )

        # 4. 해당 월의 모든 날짜 생성
        _, last_day = monthrange(payload.year, payload.month)
        daily_activities = []

        for day in range(1, last_day + 1):
            target_date = date(payload.year, payload.month, day)
            day_data = daily_map.get(target_date, {"solved": [], "will_solve": []})

            daily_activities.append(DailyActivityQuery(
                target_date=target_date,
                solved_problems=day_data["solved"],
                will_solve_problems=day_data["will_solve"]
            ))

        # 5. 전체 문제 수 계산
        total_problem_ids = set()
        for day_data in daily_map.values():
            total_problem_ids.update(p.problem_id for p in day_data["solved"])
            total_problem_ids.update(p.problem_id for p in day_data["will_solve"])

        return MonthlyActivityDataQuery(
            daily_activities=daily_activities,
            total_problem_count=len(total_problem_ids)
        )

    @transactional
    async def update_will_solve_problems(
        self,
        command: UpdateWillSolveProblemsCommand
    ):
        # 1. 입력값 정합성 검증 (순서 및 중복 체크)
        self._validate_order_consistency(command.problem_ids)

        user_id = UserAccountId(command.user_account_id)

        # 활성 BJ 계정 조회
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)
        bj_account_id_str = bj_account.bj_account_id.value if bj_account else None

        # 2. 이미 푼 문제로 등록된 경우 검증 (problem_history 기반 - Req 4)
        if bj_account and command.problem_ids:
            solved_in_history = await self.problem_history_repository.find_solved_ids_in_list(
                bj_account.bj_account_id,
                command.problem_ids
            )
            if solved_in_history:
                raise APIException(ErrorCode.ALREADY_SOLVED_PROBLEM, "이미 푼 문제입니다.")

        # 3. 해당 날짜의 모든 WILL_SOLVE 데이터를 가져옵니다.
        existing_problems = await self.user_activity_repository.find_will_solve_problems_by_date(
            user_id, command.solved_date
        )

        existing_map = {p.problem_id.value: p for p in existing_problems}
        new_problem_ids = command.problem_ids
        processed_entities = []

        # 4. 요청된 순서(index)대로 처리
        for index, p_id in enumerate(new_problem_ids):
            if p_id in existing_map:
                target = existing_map.pop(p_id)
                target.change_order(index)
                processed_entities.append(target)
            else:
                new_item = UserProblemStatus.create_will_solve(
                    user_account_id=user_id,
                    problem_id=ProblemId(p_id),
                    marked_date=command.solved_date,
                    bj_account_id=bj_account_id_str
                )
                new_item.change_order(index)
                processed_entities.append(new_item)

        # 5. 요청 리스트에 없는 기존 데이터는 삭제 처리
        for leftover in existing_map.values():
            leftover.delete()
            processed_entities.append(leftover)

        # 6. Repository를 통해 일괄 저장
        await self.user_activity_repository.save_all_will_solve_problems(processed_entities)

    @transactional
    async def update_solved_problems(
        self,
        command: UpdateSolvedProblemsCommand
    ):
        # 1. 입력값 정합성 검증
        self._validate_order_consistency(command.problem_ids)

        user_id = UserAccountId(command.user_account_id)

        # 활성 BJ 계정 조회
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)
        bj_account_id_str = bj_account.bj_account_id.value if bj_account else None

        # 1.5. problem_history 검증: bj_account가 있는 경우 실제로 푼 문제만 허용 (batch 로직과 동일)
        effective_problem_ids = command.problem_ids
        if command.problem_ids and bj_account:
            valid_ids = await self.problem_history_repository.find_solved_ids_in_list(
                bj_account.bj_account_id,
                command.problem_ids
            )
            effective_problem_ids = [pid for pid in command.problem_ids if pid in valid_ids]

        # 1.6. problem 테이블 보장 (FK 제약: problem_history.problem_id → problem.problem_id)
        if effective_problem_ids and self.problem_update_service:
            effective_problem_ids = await self.problem_update_service.ensure_problems_exist(effective_problem_ids)

        affected_dates: set[date] = set()

        # 2. 이미 푼 문제로 등록된 경우 검증 (다른 날짜 체크)
        if effective_problem_ids:
            existing_records = await self.user_activity_repository.find_problem_records_by_problem_ids(
                user_id,
                effective_problem_ids
            )

            records_on_different_date = [
                record for record in existing_records
                if record.marked_date != command.solved_date
            ]

            if records_on_different_date:
                # 케이스 C: 더 이른 날짜로만 이동 가능 (더 최근 날짜 이동은 skip)
                records_to_move = [r for r in records_on_different_date if command.solved_date < r.marked_date]
                for record in records_to_move:
                    affected_dates.add(record.marked_date)
                    record.delete()
                if records_to_move:
                    await self.user_activity_repository.save_all_problem_records(records_to_move)

        # 3. solved로 등록 시, 해당 problem_id의 will_solve 레코드 모두 삭제
        if effective_problem_ids:
            existing_will_solves = await self.user_activity_repository.find_will_solve_problems_by_problem_ids(
                user_id,
                effective_problem_ids
            )
            for will_solve in existing_will_solves:
                will_solve.delete()
            if existing_will_solves:
                await self.user_activity_repository.save_all_will_solve_problems(existing_will_solves)

        # 4. 해당 날짜의 모든 SOLVED 데이터를 가져옵니다.
        existing_problems = await self.user_activity_repository.find_problem_records_by_date(
            user_id, command.solved_date
        )

        existing_map = {p.problem_id.value: p for p in existing_problems}
        new_problem_ids = effective_problem_ids
        processed_entities = []

        # 5. 요청된 순서(index)대로 처리
        for index, p_id in enumerate(new_problem_ids):
            if p_id in existing_map:
                target = existing_map.pop(p_id)
                target.change_order(index)
                processed_entities.append(target)
            else:
                new_item = UserProblemStatus.create_solved(
                    user_account_id=user_id,
                    problem_id=ProblemId(p_id),
                    marked_date=command.solved_date,
                    bj_account_id=bj_account_id_str
                )
                new_item.change_order(index)
                processed_entities.append(new_item)

        # 6. 요청 리스트에 없는 기존 데이터는 삭제 처리
        for leftover in existing_map.values():
            leftover.delete()
            processed_entities.append(leftover)

        # 7. Repository를 통해 일괄 저장
        await self.user_activity_repository.save_all_problem_records(processed_entities)

        # 8. Req 1: user_date_record 동기화 (영향받은 날짜의 실제 solved 개수로 갱신)
        affected_dates.add(command.solved_date)
        if bj_account_id_str:
            for d in affected_dates:
                count = await self.user_activity_repository.count_solved_by_date(
                    user_id, bj_account_id_str, d
                )
                udr = UserDateRecord.create(user_id, bj_account_id_str, d, count)
                await self.user_date_record_repository.upsert(udr)

    @transactional
    async def update_solved_and_will_solve_problems(
        self,
        command: UpdateSolvedAndWillSolveProblemsCommand
    ):
        await self.update_solved_problems(
            UpdateSolvedProblemsCommand(
                user_account_id=command.user_account_id,
                solved_date=command.solved_date,
                problem_ids=command.solved_problem_ids
            )
        )

        await self.update_will_solve_problems(
            UpdateWillSolveProblemsCommand(
                user_account_id=command.user_account_id,
                solved_date=command.solved_date,
                problem_ids=command.will_solve_problem_ids
            )
        )

    @transactional
    async def batch_create_solved_problems(
        self,
        command: BatchCreateSolvedProblemsCommand
    ):
        """
        여러 날짜의 문제를 한번에 추가 (date 기반)

        Args:
            command: 배치 생성 명령 (user_account_id, records: [(date, [문제ID들]), ...])
        """
        user_id = UserAccountId(command.user_account_id)

        # 0. 전체 문제 ID 추출 및 중복 체크
        all_problem_ids = [pid for _, pids in command.records for pid in pids]
        if len(all_problem_ids) != len(set(all_problem_ids)):
            raise APIException(ErrorCode.DUPLICATED_ORDER, "요청 내에 중복된 문제 ID가 존재합니다.")

        if not all_problem_ids:
            if self.system_log_repository is not None:
                log = SystemLog.create(
                    log_type=SystemLogType.BULK_UPDATE,
                    status=SystemLogStatus.SKIPPED,
                    log_data=BulkUpdateLogData(
                        user_account_id=command.user_account_id,
                        bj_account_id="",
                        input_records=[],
                        added_problem_ids=[],
                        affected_dates=[],
                        skipped_problem_ids=[],
                        error="입력된 문제 ID 없음",
                    ).to_dict(),
                    should_notify=False,
                )
                await self.system_log_repository.save(log)
            return

        # 1. problem_history에서 실제로 푼 문제만 필터 (안 푼 문제 skip)
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)

        valid_problem_ids: set[int] = set(all_problem_ids)
        if bj_account:
            solved_ids = await self.problem_history_repository.find_solved_ids_in_list(
                bj_account.bj_account_id,
                list(set(all_problem_ids))
            )
            valid_problem_ids = solved_ids

        # 1.5. problem 테이블 보장 (FK 제약: problem_history.problem_id → problem.problem_id)
        if valid_problem_ids and self.problem_update_service:
            valid_list = await self.problem_update_service.ensure_problems_exist(list(valid_problem_ids))
            valid_problem_ids = set(valid_list)

        # Req 2: 문제ID → 요청된 날짜 매핑 (동일 pid는 가장 이른 날짜 우선)
        requested_date_map: dict[int, date] = {}
        for target_date, pids in command.records:
            for pid in pids:
                if pid in valid_problem_ids:
                    if pid not in requested_date_map or target_date < requested_date_map[pid]:
                        requested_date_map[pid] = target_date

        # 2. 기존 SOLVED 레코드 조회
        existing_records = await self.user_activity_repository.find_problem_records_by_problem_ids(
            user_id,
            list(valid_problem_ids)
        )

        # 다른 날짜에 이미 등록된 문제 → 방향 검증 후 기존 삭제
        records_on_different_date = [
            status for status in existing_records
            if status.marked_date != requested_date_map.get(status.problem_id.value)
        ]

        affected_dates: set[date] = set()
        if records_on_different_date:
            # 더 이른 날짜로만 이동 가능 (더 최근 날짜 이동은 skip)
            records_to_move = [
                s for s in records_on_different_date
                if requested_date_map[s.problem_id.value] < s.marked_date
            ]
            # skip된 pid는 requested_date_map에서 제거해 새 레코드 생성 방지
            skipped_pids = {
                s.problem_id.value for s in records_on_different_date
                if requested_date_map[s.problem_id.value] >= s.marked_date
            }
            for pid in skipped_pids:
                requested_date_map.pop(pid, None)
            for status in records_to_move:
                affected_dates.add(status.marked_date)
                status.delete()
            if records_to_move:
                await self.user_activity_repository.save_all_problem_records(records_to_move)

        # 3. will_solve 삭제 처리
        existing_will_solves = await self.user_activity_repository.find_will_solve_problems_by_problem_ids(
            user_id,
            list(valid_problem_ids)
        )
        for will_solve in existing_will_solves:
            will_solve.delete()
        if existing_will_solves:
            await self.user_activity_repository.save_all_will_solve_problems(existing_will_solves)

        # 4. 이미 동일 날짜에 등록된 문제 ID 집합 생성 (중복 생성 방지)
        existing_same_date_pids: set[int] = set()
        for status in existing_records:
            pid = status.problem_id.value
            if pid in requested_date_map and status.marked_date == requested_date_map[pid]:
                existing_same_date_pids.add(pid)

        # 5. 날짜별로 새 레코드 생성 (requested_date_map 기준으로 deduplicate된 날짜 사용)
        all_new_records = []
        # pid별 실제 적용 날짜로 그룹화
        date_to_pids: dict[date, list[int]] = {}
        for pid, target_date in requested_date_map.items():
            date_to_pids.setdefault(target_date, []).append(pid)

        for target_date, pids in date_to_pids.items():
            existing_on_date = await self.user_activity_repository.find_problem_records_by_date(
                user_id, target_date
            )
            max_order = max((s.order for s in existing_on_date), default=-1)

            order_offset = 0
            for pid in pids:
                if pid in existing_same_date_pids:
                    continue  # 동일 날짜 중복 방지

                new_record = UserProblemStatus.create_solved(
                    user_account_id=user_id,
                    problem_id=ProblemId(pid),
                    marked_date=target_date,
                    bj_account_id=bj_account.bj_account_id.value if bj_account else None
                )
                new_record.change_order(max_order + 1 + order_offset)
                all_new_records.append(new_record)
                affected_dates.add(target_date)
                order_offset += 1

        # 6. 일괄 저장
        if all_new_records:
            await self.user_activity_repository.save_all_problem_records(all_new_records)

        # 7. Req 1: user_date_record 동기화 (영향받은 날짜의 실제 solved 개수로 갱신)
        bj_account_id_str = bj_account.bj_account_id.value if bj_account else None
        if bj_account_id_str and affected_dates:
            for d in affected_dates:
                count = await self.user_activity_repository.count_solved_by_date(
                    user_id, bj_account_id_str, d
                )
                udr = UserDateRecord.create(user_id, bj_account_id_str, d, count)
                await self.user_date_record_repository.upsert(udr)

        # 8. BULK_UPDATE system_log 저장
        if self.system_log_repository is not None:
            added_problem_ids = [r.problem_id.value for r in all_new_records]
            skipped_ids = list(valid_problem_ids - set(added_problem_ids) - {
                s.problem_id.value for s in existing_records
                if s.problem_id.value in requested_date_map
                and s.marked_date == requested_date_map.get(s.problem_id.value)
            })
            input_records_serialized = [
                [d.isoformat(), pids]
                for d, pids in command.records
            ]
            log_status = SystemLogStatus.SUCCESS if added_problem_ids else SystemLogStatus.SKIPPED
            log = SystemLog.create(
                log_type=SystemLogType.BULK_UPDATE,
                status=log_status,
                log_data=BulkUpdateLogData(
                    user_account_id=command.user_account_id,
                    bj_account_id=bj_account.bj_account_id.value if bj_account else "",
                    input_records=input_records_serialized,
                    added_problem_ids=added_problem_ids,
                    affected_dates=[d.isoformat() for d in affected_dates],
                    skipped_problem_ids=skipped_ids,
                    error=None,
                ).to_dict(),
                should_notify=False,
            )
            await self.system_log_repository.save(log)

        # 9. 배치 동기화 완료 이벤트 발행
        sync_event = DomainEvent(
            event_type="BATCH_SYNC_COMPLETED",
            data=MarkSyncedCommand(user_account_id=command.user_account_id),
            result_type=None
        )
        await self.domain_event_bus.publish(sync_event)

    @transactional
    async def ban_tag(self, command: TagCustomCommand):
        event = DomainEvent(
            event_type="GET_TAG_INFO_REQUESTED",
            data=GetTagSummaryPayload(tag_code=command.tag_code),
            result_type=GetTagSummaryResultPayload
        )
        tag_info: GetTagSummaryResultPayload = await self.domain_event_bus.publish(event)

        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_tag_custom_by_user_account_id(user_id)
        print(activity.customize_tag)
        activity.customize_tag(
            tag_id=TagId(tag_info.tag_id),
            exclude=True,
            reason=ExcludedReason.INSIGNIFICANT
        )

        await self.user_activity_repository.save_tag_custom(activity)

    @transactional
    async def unban_tag(self, command: TagCustomCommand):
        event = DomainEvent(
            event_type="GET_TAG_INFO_REQUESTED",
            data=GetTagSummaryPayload(tag_code=command.tag_code),
            result_type=GetTagSummaryResultPayload
        )
        tag_info: GetTagSummaryResultPayload | None = await self.domain_event_bus.publish(event)

        if not tag_info:
            raise APIException(ErrorCode.TAG_NOT_FOUND, f"Tag with code {command.tag_code} not found.")

        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_tag_custom_by_user_account_id(user_id)

        activity.remove_tag_customization(tag_id=TagId(tag_info.tag_id))

        await self.user_activity_repository.save_tag_custom(activity)

    @transactional
    async def ban_problem(self, command: BanProblemCommand):
        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_banned_problem_by_user_account_id(user_id)

        activity.ban_problem(ProblemId(command.problem_id))

        await self.user_activity_repository.save_problem_banned_record(activity)

    @transactional
    async def unban_problem(self, command: BanProblemCommand):
        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_banned_problem_by_user_account_id(user_id)

        activity.remove_ban_problem(ProblemId(command.problem_id))
        await self.user_activity_repository.save_problem_banned_record(activity)

    def _validate_order_consistency(self, problem_ids: list[int]):
        if len(problem_ids) != len(set(problem_ids)):
            raise APIException(ErrorCode.DUPLICATED_ORDER)

    @transactional(readonly=True)
    async def get_banned_problems(self, user_account_id: int):
        user_id = UserAccountId(user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_banned_problem_by_user_account_id(user_id)

        problem_ids = activity.banned_problem_ids

        if not problem_ids:
            return BannedProblemsQuery(banned_problem_list=[])

        event = DomainEvent(
            event_type="GET_PROBLEM_INFOS_REQUESTED",
            data=GetProblemsInfoPayload(problem_ids=[problem_id.value for problem_id in problem_ids]),
            result_type=ProblemsInfoQuery
        )
        problems_info: ProblemsInfoQuery | None = await self.domain_event_bus.publish(event)

        if not problems_info:
            return BannedProblemsQuery(banned_problem_list=[])

        banned_problem_list = list(problems_info.problems.values())
        return BannedProblemsQuery(banned_problem_list=banned_problem_list)

    @transactional(readonly=True)
    async def get_banned_tags(self, user_account_id: int):
        user_id = UserAccountId(user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_tag_custom_by_user_account_id(user_id)

        excluded_tag_ids = activity.excluded_tag_ids

        if not excluded_tag_ids:
            return BannedTagsQuery(banned_tag_list=[])

        event = DomainEvent(
            event_type="GET_TAG_INFOS_REQUESTED",
            data=GetTagSummarysPayload(tag_ids=list(excluded_tag_ids)),
            result_type=GetTagSummarysResultPayload
        )
        result: GetTagSummarysResultPayload | None = await self.domain_event_bus.publish(event)

        if not result:
            return BannedTagsQuery(banned_tag_list=[])

        return BannedTagsQuery(banned_tag_list=result.tags)

    @event_handler("USER_ACCOUNT_WITHDRAWAL_REQUESTED")
    @transactional
    async def delete_user_activity(
        self,
        command: DeleteUserActivityCommand
    ) -> bool:
        user_account_id = UserAccountId(command.user_account_id)
        await self.user_activity_repository.delete_all_by_user_account_id(user_account_id)
        logger.info(f"UserActivity 데이터 삭제 완료: user_id={command.user_account_id}")
        return True

    @transactional
    async def set_problem_representative_tag(
        self,
        command: SetProblemRepresentativeTagCommand
    ):
        """문제의 대표 태그 설정"""
        user_id = UserAccountId(command.user_account_id)

        # 1. 두 엔티티 모두 조회
        problem_record = await self.user_activity_repository.find_problem_record_by_problem_id(
            user_id, command.problem_id
        )
        will_solve_problem = await self.user_activity_repository.find_will_solve_problem_by_problem_id(
            user_id, command.problem_id
        )

        # 2. 둘 다 없으면 에러 (streak 기반 fallback 제거)
        if not problem_record and not will_solve_problem:
            raise APIException(
                ErrorCode.INVALID_REQUEST,
                f"문제 기록을 찾을 수 없습니다. problem_id={command.problem_id}"
            )

        # 3. tag_code가 있으면 tag_id로 변환 및 문제 태그 검증
        tag_id = None
        if command.representative_tag_code:
            event = DomainEvent(
                event_type="GET_TAG_INFO_REQUESTED",
                data=GetTagSummaryPayload(tag_code=command.representative_tag_code),
                result_type=GetTagSummaryResultPayload
            )
            tag_info: GetTagSummaryResultPayload = await self.domain_event_bus.publish(event)

            if not tag_info:
                raise APIException(
                    ErrorCode.INVALID_REQUEST,
                    f"태그를 찾을 수 없습니다. tag_code={command.representative_tag_code}"
                )

            problem_info_event = DomainEvent(
                event_type="GET_PROBLEM_INFOS_REQUESTED",
                data=GetProblemsInfoPayload(problem_ids=[command.problem_id]),
                result_type=ProblemsInfoQuery
            )
            problems_info: ProblemsInfoQuery = await self.domain_event_bus.publish(problem_info_event)

            if problems_info and command.problem_id in problems_info.problems:
                problem_info = problems_info.problems[command.problem_id]
                problem_tag_codes = {tag.tag_code for tag in problem_info.tags}

                if command.representative_tag_code not in problem_tag_codes:
                    raise APIException(
                        ErrorCode.INVALID_REQUEST,
                        f"해당 태그는 문제의 태그 목록에 포함되지 않습니다. tag_code={command.representative_tag_code}"
                    )

            tag_id = TagId(tag_info.tag_id)

        # 4. 존재하는 엔티티에 대표 태그 설정 및 저장
        if problem_record:
            problem_record.set_representative_tag(tag_id)
            await self.user_activity_repository.save_problem_status(problem_record)

        if will_solve_problem:
            will_solve_problem.set_representative_tag(tag_id)
            await self.user_activity_repository.save_problem_status(will_solve_problem)
