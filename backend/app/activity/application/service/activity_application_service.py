"""Activity Application Service"""
import logging
from calendar import monthrange
from collections import defaultdict
from datetime import date

from app.activity.application.command.tag_custom_command import TagCustomCommand
from app.activity.application.command.update_will_solve_problems import UpdateWillSolveProblemsCommand
from app.activity.application.query.monthly_activity_data_query import (
    DailyActivityQuery,
    MonthlyActivityDataQuery
)
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.domain.event.payloads import GetTagSummaryPayload, GetTagSummaryResultPayload
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.event.get_monthly_activity_data_payload import GetMonthlyActivityDataPayload
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
        domain_event_bus: DomainEventBus
    ):
        self.user_activity_repository = user_activity_repository
        self.domain_event_bus = domain_event_bus

    @event_handler("GET_MONTHLY_ACTIVITY_DATA_REQUESTED")
    @transactional
    async def get_monthly_activity_data(
        self,
        payload: GetMonthlyActivityDataPayload
    ) -> MonthlyActivityDataQuery:
        """
        월간 활동 데이터 조회
        Args:
            payload: 월간 활동 데이터 조회 요청
        Returns:
            MonthlyActivityDataQuery: 월간 활동 데이터
        """
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

        # 3. 날짜별로 그룹화
        daily_map = defaultdict(lambda: {"solved": set(), "will_solve": set()})

        for record in problem_records:
            if record.solved:
                daily_map[record.marked_date]["solved"].add(record.problem_id.value)

        for will_solve in will_solve_problems:
            daily_map[will_solve.marked_date]["will_solve"].add(will_solve.problem_id.value)

        # 4. 해당 월의 모든 날짜 생성 (데이터가 없는 날도 포함)
        _, last_day = monthrange(payload.year, payload.month)
        daily_activities = []

        for day in range(1, last_day + 1):
            target_date = date(payload.year, payload.month, day)
            day_data = daily_map.get(target_date, {"solved": set(), "will_solve": set()})

            daily_activities.append(DailyActivityQuery(
                target_date=target_date,
                solved_problem_ids=list(day_data["solved"]),
                will_solve_problem_ids=list(day_data["will_solve"])
            ))

        # 5. 전체 문제 수 계산
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
        
        # 1. 해당 날짜의 모든 데이터(삭제된 것 포함)를 가져옵니다. 
        # (나중에 복구를 위해 deleted_at 포함 조회를 권장)
        existing_problems = await self.user_activity_repository.find_will_solve_problems_by_date(
            user_id, command.solved_date
        )
        
        existing_map = {p.problem_id.value: p for p in existing_problems}
        new_problem_ids = command.problem_ids
        processed_entities = []

        # 2. 요청된 순서(index)대로 처리
        for index, p_id in enumerate(new_problem_ids):
            if p_id in existing_map:
                target = existing_map.pop(p_id)
                # 만약 삭제되었던 문제라면 복구
                if target.deleted_at:
                    target.restore()
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

        # 3. 요청 리스트에 없는데 기존 DB에 살아있는(deleted_at is None) 데이터들은 삭제 처리
        for leftover in existing_map.values():
            if leftover.deleted_at is None:
                leftover.delete()
                processed_entities.append(leftover)

        # 4. Repository를 통해 일괄 저장
        await self.user_activity_repository.save_all_will_solve_problems(processed_entities)

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
        
    def _validate_order_consistency(self, problem_ids: list[int]):
        # 중복된 ID가 포함되어 있는지 체크
        if len(problem_ids) != len(set(problem_ids)):
            raise APIException(ErrorCode.DUPLICATED_ORDER)