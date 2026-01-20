"""Activity Application Service"""
import logging
from calendar import monthrange
from collections import defaultdict
from datetime import date

from app.activity.application.command.ban_problem_command import BanProblemCommand
from app.activity.application.command.tag_custom_command import TagCustomCommand
from app.activity.application.command.update_solved_problems_command import UpdateSolvedProblemsCommand
from app.activity.application.command.update_solved_will_solve_problems_command import UpdateSolvedAndWillSolveProblemsCommand
from app.activity.application.command.update_will_solve_problems import UpdateWillSolveProblemsCommand
from app.activity.application.query.banned_list_query import BannedProblemsQuery, BannedTagsQuery
from app.activity.application.query.monthly_activity_data_query import (
    DailyActivityQuery,
    MonthlyActivityDataQuery
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
    @transactional
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
        # print(will_solve_problems)
        # 3. 날짜별로 그룹화 (set 대신 list 사용)
        # 순서를 보존하기 위해 list를 사용합니다.
        daily_map = defaultdict(lambda: {"solved": [], "will_solve": []})

        for record in problem_records:
            if record.solved:
                pid = record.problem_id.value
                # 중복 체크를 하며 리스트에 추가 (이미 정렬된 순서 유지)
                if pid not in daily_map[record.marked_date]["solved"]:
                    daily_map[record.marked_date]["solved"].append(pid)

        for will_solve in will_solve_problems:
            pid = will_solve.problem_id.value
            # 중복 체크를 하며 리스트에 추가 (이미 정렬된 순서 유지)
            if pid not in daily_map[will_solve.marked_date]["will_solve"]:
                daily_map[will_solve.marked_date]["will_solve"].append(pid)

        # 4. 해당 월의 모든 날짜 생성
        _, last_day = monthrange(payload.year, payload.month)
        daily_activities = []

        for day in range(1, last_day + 1):
            target_date = date(payload.year, payload.month, day)
            # 이미 3번에서 list로 만들었으므로 그대로 사용합니다.
            day_data = daily_map.get(target_date, {"solved": [], "will_solve": []})

            daily_activities.append(DailyActivityQuery(
                target_date=target_date,
                solved_problem_ids=day_data["solved"],
                will_solve_problem_ids=day_data["will_solve"]
            ))

        # 5. 전체 문제 수 계산 (고유 ID 수이므로 여기선 set을 써도 무방)
        total_problem_ids = set()
        for day_data in daily_map.values():
            total_problem_ids.update(day_data["solved"])
            total_problem_ids.update(day_data["will_solve"])

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

        # 2. 백준 계정 조회 (이미 푼 문제 검증을 위해)
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)
        if bj_account and command.problem_ids:
            # 이미 푼 문제 목록 조회
            solved_problem_ids = await self.problem_history_repository.find_solved_ids_in_list(
                bj_account.bj_account_id,
                command.problem_ids
            )
            # 추가하려는 문제 중 이미 푼 문제가 있으면 에러
            if solved_problem_ids:
                raise APIException(
                    ErrorCode.ALREADY_SOLVED_PROBLEM,
                    f"이미 해결한 문제입니다."
                )

        # 3. 해당 날짜의 모든 데이터(삭제된 것 포함)를 가져옵니다.
        # (나중에 복구를 위해 deleted_at 포함 조회를 권장)
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

        # 5. 요청 리스트에 없는데 기존 DB에 살아있는(deleted_at is None) 데이터들은 삭제 처리
        for leftover in existing_map.values():
            if leftover.deleted_at is None:
                leftover.delete()
                processed_entities.append(leftover)

        # 6. Repository를 통해 일괄 저장
        await self.user_activity_repository.save_all_will_solve_problems(processed_entities)
    
    @transactional
    async def update_solved_problems(
        self,
        command: UpdateSolvedProblemsCommand
    ):

        # 1. 입력값 정합성 검증 (순서 및 중복 체크)
        self._validate_order_consistency(command.problem_ids)

        user_id = UserAccountId(command.user_account_id)

        # 2. 백준 계정 조회 및 검증
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_id)
        if bj_account and command.problem_ids:
            # 해당 문제들의 problem_history를 streak과 함께 조회
            problem_histories = await self.problem_history_repository.find_by_problem_ids_with_streak(
                bj_account.bj_account_id,
                command.problem_ids
            )

            # problem_id별로 매핑
            problem_history_map = {ph.problem_id.value: ph for ph in problem_histories}

            # 추가하려는 문제 중 다른 날짜에 streak이 있는 문제가 있으면 에러
            for p_id in command.problem_ids:
                if p_id in problem_history_map:
                    ph = problem_history_map[p_id]
                    # streak_date가 있고, 요청 날짜와 다르면 에러
                    if ph.streak_date is not None and ph.streak_date != command.solved_date:
                        raise APIException(
                            ErrorCode.PROBLEM_ALREADY_RECORDED_ON_DIFFERENT_DATE,
                            f"이미 기록된 문제입니다."
                        )

        # 3. 해당 날짜의 모든 데이터(삭제된 것 포함)를 가져옵니다.
        # (나중에 복구를 위해 deleted_at 포함 조회를 권장)
        existing_problems = await self.user_activity_repository.find_problem_records_by_date(
            user_id, command.solved_date
        )

        existing_map = {p.problem_id.value: p for p in existing_problems}
        new_problem_ids = command.problem_ids
        processed_entities = []

        # 4. 요청된 순서(index)대로 처리
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

        # 5. 요청 리스트에 없는데 기존 DB에 살아있는(deleted_at is None) 데이터들은 삭제 처리
        for leftover in existing_map.values():
            if leftover.deleted_at is None:
                leftover.delete()
                processed_entities.append(leftover)

        # 6. Repository를 통해 일괄 저장
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
        
    @transactional
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
    
    @transactional
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