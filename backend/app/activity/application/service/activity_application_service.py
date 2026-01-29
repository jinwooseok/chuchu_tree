"""Activity Application Service"""
import logging
from calendar import monthrange
from collections import defaultdict
from datetime import date

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
from app.activity.domain.entity.problem_record import ProblemRecord
from app.problem.application.query.problems_info_query import ProblemsInfoQuery
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.domain.event.payloads import GetProblemsInfoPayload, GetTagSummaryPayload, GetTagSummaryResultPayload, GetTagSummarysPayload, GetTagSummarysResultPayload
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.event.get_monthly_activity_data_payload import GetMonthlyActivityDataPayload
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import ExcludedReason
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId
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
        problem_history_repository: ProblemHistoryRepository
    ):
        self.user_activity_repository = user_activity_repository
        self.domain_event_bus = domain_event_bus
        self.baekjoon_account_repository = baekjoon_account_repository
        self.problem_history_repository = problem_history_repository

    @event_handler("GET_MONTHLY_ACTIVITY_DATA_REQUESTED")
    @transactional(readonly=True)
    async def get_monthly_activity_data(
        self,
        payload: GetMonthlyActivityDataPayload
    ) -> MonthlyActivityDataQuery:
        user_account_id = UserAccountId(payload.user_account_id)

        # 1. 월간 푼 문제 기록 조회 (Repository에서 이미 ORDER BY 정렬되어 있어야 함)
        problem_records = await self.user_activity_repository.find_monthly_problem_records(
            user_id=user_account_id,
            year=payload.year,
            month=payload.month
        )

        # 2. 월간 풀 예정 문제 조회 (Repository에서 이미 ORDER BY 정렬되어 있어야 함)
        will_solve_problems = await self.user_activity_repository.find_monthly_will_solve_problems(
            user_id=user_account_id,
            year=payload.year,
            month=payload.month
        )
        # 3. 날짜별로 그룹화 (ProblemActivityInfo 사용)
        # 순서를 보존하기 위해 list를 사용합니다.
        daily_map = defaultdict(lambda: {"solved": [], "will_solve": []})
        seen_solved = defaultdict(set)  # 날짜별 중복 체크용
        seen_will_solve = defaultdict(set)

        for record in problem_records:
            if record.solved:
                pid = record.problem_id.value
                # 중복 체크를 하며 리스트에 추가 (이미 정렬된 순서 유지)
                if pid not in seen_solved[record.marked_date]:
                    seen_solved[record.marked_date].add(pid)
                    rep_tag_id = record.representative_tag_id.value if record.representative_tag_id else None
                    daily_map[record.marked_date]["solved"].append(
                        ProblemActivityInfo(problem_id=pid, representative_tag_id=rep_tag_id)
                    )

        for will_solve in will_solve_problems:
            pid = will_solve.problem_id.value
            # 중복 체크를 하며 리스트에 추가 (이미 정렬된 순서 유지)
            if pid not in seen_will_solve[will_solve.marked_date]:
                seen_will_solve[will_solve.marked_date].add(pid)
                rep_tag_id = will_solve.representative_tag_id.value if will_solve.representative_tag_id else None
                daily_map[will_solve.marked_date]["will_solve"].append(
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

        # 5. 전체 문제 수 계산 (고유 ID 수이므로 여기선 set을 써도 무방)
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

        # 2. 백준 계정 조회 및 검증 - streak이 있고 다른 날짜에 기록된 문제인지 확인
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)
        if bj_account and command.problem_ids:
            # streak 정보와 함께 문제 이력 조회
            problem_histories = await self.problem_history_repository.find_by_problem_ids_with_streak(
                bj_account.bj_account_id,
                command.problem_ids
            )
            # streak이 있고 다른 날짜에 기록된 문제만 필터링
            conflicting = [
                ph for ph in problem_histories
                if ph.streak_id is not None and ph.streak_date != command.solved_date
            ]
            if conflicting:
                raise APIException(
                    ErrorCode.ALREADY_SOLVED_PROBLEM,
                    f"이미 다른 날짜에 스트릭으로 기록된 문제입니다."
                )

        # 3. 이미 푼 문제로 등록된 경우 검증
        if command.problem_ids:
            # 해당 문제들의 problem_record 조회 (모든 날짜)
            existing_records = await self.user_activity_repository.find_problem_records_by_problem_ids(
                user_id,
                command.problem_ids
            )

            # 푼 문제로 이미 등록된 문제가 있으면 에러
            if existing_records:
                raise APIException(
                    ErrorCode.PROBLEM_ALREADY_RECORDED_ON_DIFFERENT_DATE,
                    f"이미 기록된 문제입니다."
                )

        # 4. 해당 날짜의 모든 데이터(삭제된 것 포함)를 가져옵니다.
        # (나중에 복구를 위해 deleted_at 포함 조회를 권장)
        existing_problems = await self.user_activity_repository.find_will_solve_problems_by_date(
            user_id, command.solved_date
        )

        existing_map = {p.problem_id.value: p for p in existing_problems}
        new_problem_ids = command.problem_ids
        processed_entities = []

        # 5. 요청된 순서(index)대로 처리
        for index, p_id in enumerate(new_problem_ids):
            if p_id in existing_map:
                target = existing_map.pop(p_id)
                # 순서 변경 (메서드 내부에서 변경 여부 체크)
                target.change_order(index)
                processed_entities.append(target)
            else:
                # 신규 생성
                new_item: WillSolveProblem = WillSolveProblem.create(
                    user_account_id=user_id,
                    problem_id=ProblemId(p_id),
                    marked_date=command.solved_date
                )
                new_item.change_order(index)
                processed_entities.append(new_item)

        # 6. 요청 리스트에 없는데 기존 DB에 살아있는(deleted_at is None) 데이터들은 삭제 처리
        for leftover in existing_map.values():
            if leftover.deleted_at is None:
                leftover.delete()
                processed_entities.append(leftover)

        # 7. Repository를 통해 일괄 저장
        await self.user_activity_repository.save_all_will_solve_problems(processed_entities)
    
    @transactional
    async def update_solved_problems(
        self,
        command: UpdateSolvedProblemsCommand
    ):

        # 1. 입력값 정합성 검증 (순서 및 중복 체크)
        self._validate_order_consistency(command.problem_ids)

        user_id = UserAccountId(command.user_account_id)

        # 2. 백준 계정 조회 및 검증 - streak이 있고 다른 날짜에 기록된 문제인지 확인
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)
        if bj_account and command.problem_ids:
            # streak 정보와 함께 문제 이력 조회
            problem_histories = await self.problem_history_repository.find_by_problem_ids_with_streak(
                bj_account.bj_account_id,
                command.problem_ids
            )
            # streak이 있고 다른 날짜에 기록된 문제만 필터링
            conflicting = [
                ph for ph in problem_histories
                if ph.streak_id is not None and ph.streak_date != command.solved_date
            ]
            if conflicting:
                raise APIException(
                    ErrorCode.ALREADY_SOLVED_PROBLEM,
                    f"이미 다른 날짜에 스트릭으로 기록된 문제입니다."
                )

        # 3. 이미 푼 문제로 등록된 경우 검증 - 케이스 C, D 처리
        if command.problem_ids:
            # 해당 문제들의 problem_record 조회 (모든 날짜)
            existing_records = await self.user_activity_repository.find_problem_records_by_problem_ids(
                user_id,
                command.problem_ids
            )

            # 다른 날짜에 이미 등록된 문제 필터링
            records_on_different_date = [
                record for record in existing_records
                if record.marked_date != command.solved_date
            ]

            if records_on_different_date:
                # streak 연동 여부 확인을 위해 problem_history 조회
                problem_ids_to_check = [r.problem_id.value for r in records_on_different_date]

                # bj_account가 있으면 streak 확인
                streak_date_map: dict[int, date] = {}
                if bj_account:
                    streak_histories = await self.problem_history_repository.find_by_problem_ids_with_streak(
                        bj_account.bj_account_id,
                        problem_ids_to_check
                    )
                    # streak이 연동된 문제들의 날짜 매핑
                    streak_date_map = {
                        ph.problem_id.value: ph.streak_date
                        for ph in streak_histories
                        if ph.streak_id is not None and ph.streak_date is not None
                    }

                records_to_delete = []
                for record in records_on_different_date:
                    pid = record.problem_id.value
                    streak_date = streak_date_map.get(pid)

                    # 케이스 D: 다른 날에 solved_problem 존재 + streak 날짜와 일치 → 불가능
                    if streak_date and record.marked_date == streak_date:
                        raise APIException(
                            ErrorCode.PROBLEM_ALREADY_RECORDED_ON_DIFFERENT_DATE,
                            f"스트릭과 연동된 기록은 날짜를 변경할 수 없습니다."
                        )

                    # 케이스 C: 다른 날에 solved_problem만 존재 (streak 연동 없음) → 가능 (기존 삭제 후 새로 생성)
                    if record.deleted_at is None:
                        record.delete()
                        records_to_delete.append(record)

                # 케이스 C에 해당하는 기존 레코드 삭제 처리
                if records_to_delete:
                    await self.user_activity_repository.save_all_problem_records(records_to_delete)

        # 3-1. solved로 등록 시, 해당 problem_id의 will_solve 레코드 모두 삭제 처리
        if command.problem_ids:
            existing_will_solves = await self.user_activity_repository.find_will_solve_problems_by_problem_ids(
                user_id,
                command.problem_ids
            )
            # 기존 will_solve 삭제 처리
            for will_solve in existing_will_solves:
                if will_solve.deleted_at is None:
                    will_solve.delete()
            if existing_will_solves:
                await self.user_activity_repository.save_all_will_solve_problems(existing_will_solves)

        # 4. 해당 날짜의 모든 데이터(삭제된 것 포함)를 가져옵니다.
        existing_problems = await self.user_activity_repository.find_problem_records_by_date(
            user_id, command.solved_date
        )

        existing_map = {p.problem_id.value: p for p in existing_problems}
        new_problem_ids = command.problem_ids
        processed_entities = []

        # 5. 요청된 순서(index)대로 처리
        for index, p_id in enumerate(new_problem_ids):
            if p_id in existing_map:
                target = existing_map.pop(p_id)
                # 순서 변경 (메서드 내부에서 변경 여부 체크)
                target.change_order(index)
                processed_entities.append(target)
            else:
                # 신규 생성
                new_item: ProblemRecord = ProblemRecord.create(
                    user_account_id=user_id,
                    problem_id=ProblemId(p_id),
                    marked_date=command.solved_date
                )
                new_item.change_order(index)
                processed_entities.append(new_item)

        # 6. 요청 리스트에 없는데 기존 DB에 살아있는(deleted_at is None) 데이터들은 삭제 처리
        for leftover in existing_map.values():
            if leftover.deleted_at is None:
                leftover.delete()
                processed_entities.append(leftover)

        # 7. Repository를 통해 일괄 저장
        await self.user_activity_repository.save_all_problem_records(processed_entities)

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
        여러 날짜의 문제를 한번에 추가 (기존 레코드 유지, 새 레코드만 추가)

        Args:
            command: 배치 생성 명령 (user_account_id, records: [(날짜, [문제ID들]), ...])
        """
        user_id = UserAccountId(command.user_account_id)

        # 0. 전체 문제 ID 추출 및 중복 체크
        all_problem_ids = [pid for _, pids in command.records for pid in pids]
        if len(all_problem_ids) != len(set(all_problem_ids)):
            raise APIException(ErrorCode.DUPLICATED_ORDER, "요청 내에 중복된 문제 ID가 존재합니다.")

        if not all_problem_ids:
            return  # 빈 요청이면 바로 종료

        # 1. 백준 계정 조회 및 검증 - streak이 있고 다른 날짜에 기록된 문제인지 확인
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)

        # 문제ID -> 요청된 날짜 매핑
        requested_date_map: dict[int, date] = {}
        for solved_date, problem_ids in command.records:
            for pid in problem_ids:
                requested_date_map[pid] = solved_date

        if bj_account:
            # streak 정보와 함께 문제 이력 조회
            problem_histories = await self.problem_history_repository.find_by_problem_ids_with_streak(
                bj_account.bj_account_id,
                all_problem_ids
            )
            # 케이스 A: streak이 있고 다른 날짜에 기록된 문제만 필터링
            conflicting = [
                ph for ph in problem_histories
                if ph.streak_id is not None and ph.streak_date != requested_date_map.get(ph.problem_id.value)
            ]
            if conflicting:
                raise APIException(
                    ErrorCode.ALREADY_SOLVED_PROBLEM,
                    f"이미 다른 날짜에 스트릭으로 기록된 문제입니다."
                )

        # 2. 케이스 C, D 검증: 이미 푼 문제로 등록된 경우 처리
        existing_records = await self.user_activity_repository.find_problem_records_by_problem_ids(
            user_id,
            all_problem_ids
        )

        # 다른 날짜에 이미 등록된 문제 필터링
        records_on_different_date = [
            record for record in existing_records
            if record.marked_date != requested_date_map.get(record.problem_id.value)
        ]

        if records_on_different_date:
            problem_ids_to_check = [r.problem_id.value for r in records_on_different_date]

            # streak 확인
            streak_date_map: dict[int, date] = {}
            if bj_account:
                streak_histories = await self.problem_history_repository.find_by_problem_ids_with_streak(
                    bj_account.bj_account_id,
                    problem_ids_to_check
                )
                streak_date_map = {
                    ph.problem_id.value: ph.streak_date
                    for ph in streak_histories
                    if ph.streak_id is not None and ph.streak_date is not None
                }

            records_to_delete = []
            for record in records_on_different_date:
                pid = record.problem_id.value
                streak_date = streak_date_map.get(pid)

                # 케이스 D: 다른 날에 solved_problem 존재 + streak 날짜와 일치 → 불가능
                if streak_date and record.marked_date == streak_date:
                    raise APIException(
                        ErrorCode.PROBLEM_ALREADY_RECORDED_ON_DIFFERENT_DATE,
                        f"스트릭과 연동된 기록은 날짜를 변경할 수 없습니다."
                    )

                # 케이스 C: 다른 날에 solved_problem만 존재 (streak 연동 없음) → 가능 (기존 삭제 후 새로 생성)
                if record.deleted_at is None:
                    record.delete()
                    records_to_delete.append(record)

            if records_to_delete:
                await self.user_activity_repository.save_all_problem_records(records_to_delete)

        # 3. will_solve 삭제 처리: solved로 등록되는 문제의 will_solve 삭제
        existing_will_solves = await self.user_activity_repository.find_will_solve_problems_by_problem_ids(
            user_id,
            all_problem_ids
        )
        for will_solve in existing_will_solves:
            if will_solve.deleted_at is None:
                will_solve.delete()
        if existing_will_solves:
            await self.user_activity_repository.save_all_will_solve_problems(existing_will_solves)

        # 4. 이미 동일 날짜에 등록된 문제 ID 집합 생성 (중복 생성 방지)
        existing_same_date_pids: set[int] = set()
        for record in existing_records:
            if record.marked_date == requested_date_map.get(record.problem_id.value) and record.deleted_at is None:
                existing_same_date_pids.add(record.problem_id.value)

        # 5. 날짜별로 새 레코드 생성 (기존 order 뒤에 추가)
        all_new_records = []
        for solved_date, problem_ids in command.records:
            # 해당 날짜에 이미 존재하는 레코드 조회
            existing_on_date = await self.user_activity_repository.find_problem_records_by_date(
                user_id, solved_date
            )
            max_order = max((r.order for r in existing_on_date if r.deleted_at is None), default=-1)

            order_offset = 0
            for pid in problem_ids:
                # 동일 날짜에 이미 존재하면 스킵 (중복 방지)
                if pid in existing_same_date_pids:
                    continue

                new_record = ProblemRecord.create(
                    user_account_id=user_id,
                    problem_id=ProblemId(pid),
                    marked_date=solved_date
                )
                new_record.change_order(max_order + 1 + order_offset)
                all_new_records.append(new_record)
                order_offset += 1

        # 6. 일괄 저장
        if all_new_records:
            await self.user_activity_repository.save_all_problem_records(all_new_records)

    @transactional
    async def ban_tag(self, command: TagCustomCommand):
        # 1. tag code로 tag 정보 요청
        event = DomainEvent(
            event_type="GET_TAG_INFO_REQUESTED",
            data=GetTagSummaryPayload(tag_code=command.tag_code),
            result_type=GetTagSummaryResultPayload
        )
        tag_info: GetTagSummaryResultPayload = await self.domain_event_bus.publish(event)
        
        # 3. 사용자 활동 애그리거트 로드
        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_tag_custom_by_user_account_id(user_id)
        print(activity.customize_tag)
        # 4. 도메인 로직 실행
        activity.customize_tag(
            tag_id=TagId(tag_info.tag_id), 
            exclude=True,
            reason=ExcludedReason.INSIGNIFICANT 
        )
        
        # 5. 변경된 애그리거트 저장
        await self.user_activity_repository.save_tag_custom(activity)
        
    @transactional
    async def unban_tag(self, command: TagCustomCommand):
        
        # 1. tag code로 tag 정보 요청
        event = DomainEvent(
            event_type="GET_TAG_INFO_REQUESTED",
            data=GetTagSummaryPayload(tag_code=command.tag_code),
            result_type=GetTagSummaryResultPayload
        )
        tag_info: GetTagSummaryResultPayload | None = await self.domain_event_bus.publish(event)
        
        # 2. 태그 정보가 없으면 예외 처리
        if not tag_info:
            raise APIException(ErrorCode.TAG_NOT_FOUND, f"Tag with code {command.tag_code} not found.")

        # 3. 사용자 활동 애그리거트 로드
        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_tag_custom_by_user_account_id(user_id)

        # 4. 도메인 로직 실행: 태그 커스터마이징 제거
        activity.remove_tag_customization(tag_id=TagId(tag_info.tag_id))
        
        # 5. 변경된 애그리거트 저장
        await self.user_activity_repository.save_tag_custom(activity)
        
    @transactional
    async def ban_problem(self, command: BanProblemCommand):
        # 3. 사용자 활동 애그리거트 로드
        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_banned_problem_by_user_account_id(user_id)
        
        # 4. 도메인 로직 실행
        activity.ban_problem(ProblemId(command.problem_id))
        
        # 5. 변경된 애그리거트 저장
        await self.user_activity_repository.save_problem_banned_record(activity)
        
    @transactional
    async def unban_problem(self, command: BanProblemCommand):
        # 3. 사용자 활동 애그리거트 로드
        user_id = UserAccountId(command.user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_banned_problem_by_user_account_id(user_id)
        
        # 4. 도메인 로직 실행
        activity.remove_ban_problem(ProblemId(command.problem_id))
        await self.user_activity_repository.save_problem_banned_record(activity)
        
    def _validate_order_consistency(self, problem_ids: list[int]):
        # 중복된 ID가 포함되어 있는지 체크
        if len(problem_ids) != len(set(problem_ids)):
            raise APIException(ErrorCode.DUPLICATED_ORDER)

    @transactional(readonly=True)
    async def get_banned_problems(self, user_account_id: int):
        user_id = UserAccountId(user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_banned_problem_by_user_account_id(user_id)

        # 문제 id들 추출
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

        # ProblemsInfoQuery의 problems dict를 list로 변환
        banned_problem_list = list(problems_info.problems.values())
        return BannedProblemsQuery(banned_problem_list=banned_problem_list)

    @transactional(readonly=True)
    async def get_banned_tags(self, user_account_id: int):
        user_id = UserAccountId(user_account_id)
        activity: UserActivity = await self.user_activity_repository.find_only_tag_custom_by_user_account_id(user_id)

        # 제외된 태그 ID들 추출
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
        """
        사용자 활동 데이터 삭제 (Hard Delete)

        Args:
            command: 사용자 활동 데이터 삭제 명령

        Returns:
            bool: 삭제 성공 여부
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 사용자 활동 데이터 삭제 (problem_record, will_solve_problem, tag_custom, problem_banned_record)
        await self.user_activity_repository.delete_all_by_user_account_id(user_account_id)
        logger.info(f"UserActivity 데이터 삭제 완료: user_id={command.user_account_id}")

        return True

    @transactional
    async def set_problem_representative_tag(
        self,
        command: SetProblemRepresentativeTagCommand
    ):
        """
        문제의 대표 태그 설정 (자동 감지)

        solved_problem과 will_solve_problem 모두 조회하여 존재하는 엔티티에 설정.
        둘 다 없으면 problem_history에서 확인 후 새로운 problem_record 생성.

        Args:
            command: 대표 태그 설정 명령

        Raises:
            APIException: 문제를 찾을 수 없거나 태그가 유효하지 않은 경우
        """
        user_id = UserAccountId(command.user_account_id)

        # 1. 두 엔티티 모두 조회
        problem_record = await self.user_activity_repository.find_problem_record_by_problem_id(
            user_id, command.problem_id
        )
        will_solve_problem = await self.user_activity_repository.find_will_solve_problem_by_problem_id(
            user_id, command.problem_id
        )

        # 2. 둘 다 없으면 problem_history에서 확인 후 새로운 problem_record 생성
        if not problem_record and not will_solve_problem:
            bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)
            if bj_account:
                # problem_history에서 해당 문제 조회 (streak 정보 포함)
                problem_histories = await self.problem_history_repository.find_by_problem_ids_with_streak(
                    bj_account.bj_account_id,
                    [command.problem_id]
                )

                if problem_histories:
                    # streak이 있는 기록 찾기
                    history_with_streak = next(
                        (ph for ph in problem_histories if ph.streak_id is not None),
                        None
                    )

                    if history_with_streak and history_with_streak.streak_date:
                        # streak_date를 기준으로 새로운 problem_record 생성
                        problem_record = ProblemRecord.create(
                            user_account_id=user_id,
                            problem_id=ProblemId(command.problem_id),
                            marked_date=history_with_streak.streak_date,
                            solved=True
                        )

            # 여전히 없으면 에러
            if not problem_record:
                raise APIException(
                    ErrorCode.INVALID_REQUEST,
                    f"문제 기록을 찾을 수 없습니다. problem_id={command.problem_id}"
                )

        # 3. tag_code가 있으면 tag_id로 변환 및 문제 태그 검증
        tag_id = None
        if command.representative_tag_code:
            # 3-1. 태그 정보 조회
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

            # 3-2. 문제 정보 조회하여 해당 태그가 문제의 태그 목록에 포함되는지 검증
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
            await self.user_activity_repository.save_problem_record(problem_record)

        if will_solve_problem:
            will_solve_problem.set_representative_tag(tag_id)
            await self.user_activity_repository.save_will_solve_problem(will_solve_problem)