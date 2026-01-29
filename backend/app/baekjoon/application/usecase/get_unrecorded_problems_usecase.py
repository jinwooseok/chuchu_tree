import logging

from app.baekjoon.application.command.get_unrecorded_problems_command import GetUnrecordedProblemsCommand
from app.baekjoon.application.query.get_unrecorded_problems_query import GetUnrecordedProblemsQuery
from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.problem.application.query.problems_info_query import ProblemsInfoQuery


logger = logging.getLogger(__name__)


class GetUnrecordedProblemsUsecase:
    """기록되지 않은 문제 조회 Usecase

    유저가 실제로 solved.ac에서 푼 문제 중 우리 시스템에 기록되지 않은 문제들을 조회합니다.
    """

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        problem_history_repository: ProblemHistoryRepository,
        domain_event_bus: DomainEventBus
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.problem_history_repository = problem_history_repository
        self.domain_event_bus = domain_event_bus

    @transactional(readonly=True)
    async def execute(self, command: GetUnrecordedProblemsCommand) -> GetUnrecordedProblemsQuery:
        """기록되지 않은 문제 조회

        Args:
            command: 유저 계정 ID를 포함한 명령

        Returns:
            GetUnrecordedProblemsQuery: 기록되지 않은 문제 목록
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 1. 백준 계정 조회
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)
        if not bj_account:
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 2. problem_history에는 있지만 problem_record에 기록되지 않은 문제 ID 조회
        unrecorded_problem_ids = await self.problem_history_repository.find_unrecorded_problem_ids(
            user_account_id=user_account_id,
            bj_account_id=bj_account.bj_account_id
        )

        # 3. 문제가 없으면 빈 목록 반환
        if not unrecorded_problem_ids:
            return GetUnrecordedProblemsQuery(problems=[])

        # 4. 문제 상세 정보 조회 (Domain Event 사용)
        problems_info = await self._fetch_problems_info(unrecorded_problem_ids)

        # 5. Query로 변환하여 반환
        return GetUnrecordedProblemsQuery(
            problems=list(problems_info.problems.values())
        )

    async def _fetch_problems_info(self, problem_ids: set[int]) -> ProblemsInfoQuery:
        """문제 상세 정보 조회

        Args:
            problem_ids: 조회할 문제 ID 집합

        Returns:
            ProblemsInfoQuery: 문제 상세 정보
        """
        if not problem_ids:
            return ProblemsInfoQuery(problems={})

        event = DomainEvent(
            event_type="GET_PROBLEM_INFOS_REQUESTED",
            data=GetProblemsInfoPayload(problem_ids=list(problem_ids)),
            result_type=ProblemsInfoQuery
        )
        return await self.domain_event_bus.publish(event)