
import logging
from datetime import datetime, date

from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
from app.baekjoon.application.query.link_bj_account_query import LinkBaekjoonAccountResultQuery
from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.event.link_bj_account_payload import LinkBjAccountPayload
from app.baekjoon.domain.gateway.solvedac_gateway import SolvedacGateway
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemId, TierId
from app.common.infra.event.decorators import event_register_handlers, event_handler
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)


@event_register_handlers()
class LinkBjAccountUsecase:
    """
    백준 계정과 연동하는 시나리오

    1. 백준 id와 유저 계정 id를 입력 받음
    2. 백준 id가 DB에 있다면 바로 연동 후 종료. 없다면 solvedAC API로 백준 계정 히스토리를 받음
    3. 백준 계정 테이블 저장
    4. 문제 히스토리 저장
    5. 히스토리 저장 후 성공 응답 반환
    """

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        solvedac_gateway: SolvedacGateway,
        domain_event_bus: DomainEventBus
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.solvedac_gateway = solvedac_gateway
        self.domain_event_bus = domain_event_bus

    @transactional
    async def execute(
        self,
        command: LinkBjAccountCommand
    ) -> None:
        """
        백준 계정 연동 처리

        Args:
            command: 백준 계정 연동 요청 페이로드
        """

        # 1. 백준 계정이 DB에 이미 존재하는지 확인
        bj_account_id = BaekjoonAccountId(command.bj_account_id)
        existing_account = await self.baekjoon_account_repository.find_by_id(bj_account_id)
        
        event = DomainEvent(
            event_type="LINK_BAEKJOON_ACCOUNT_REQUESTED",
            data=LinkBjAccountPayload(
                user_account_id=command.user_account_id,
                bj_account_id=command.bj_account_id
            ),
            result_type=bool
        )
        
        # 2-1. 이미 존재하면 바로 반환
        if existing_account:
            
            # 2. 백준 도메인에 이벤트 발행
            await self.domain_event_bus.publish(event)
            return

        # 2-2. 존재하지 않으면 solved.ac에서 데이터 수집
        logger.info(f"[LinkBjAccountUsecase] solved.ac에서 데이터 수집 시작: {command.bj_account_id}")
        user_data = await self.solvedac_gateway.fetch_user_data(command.bj_account_id)

        if user_data is None:
            logger.error(f"[LinkBjAccountUsecase] solved.ac에서 데이터를 찾을 수 없음: {command.bj_account_id}")
            raise APIException(ErrorCode.BAEKJOON_USER_NOT_FOUND)

        # 3. BaekjoonAccount 엔티티 생성 (user_info 사용)
        baekjoon_account = BaekjoonAccount.create(
            bj_account_id=bj_account_id,
            tier_id=TierId(user_data.user_info.tier)
        )

        # 레이팅 및 통계 업데이트
        baekjoon_account.update_rating(user_data.user_info.rating)
        baekjoon_account.update_statistics(
            contribution_count=0,  # API에서 제공하지 않음
            class_level=user_data.user_info.class_level,
            longest_streak=user_data.user_info.max_streak
        )

        # 4. 문제 히스토리 기록 (시간 정보 없음)
        for problem in user_data.problems:
            baekjoon_account.record_problem_solved(
                problem_id=ProblemId(problem.problem_id)
            )

        # 5. 스트릭 히스토리 기록
        for history_item in user_data.history:
            # timestamp를 date로 변환
            try:
                timestamp_str = history_item.timestamp
                # ISO 8601 format: "2024-01-08T00:00:00Z"
                streak_date = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00')).date()
                baekjoon_account.add_streak(
                    streak_date=streak_date,
                    solved_count=history_item.solved_count
                )
            except Exception as e:
                logger.warning(f"[LinkBjAccountUsecase] 스트릭 파싱 실패: {history_item.timestamp}, {e}")
                continue

        logger.info(f"[LinkBjAccountUsecase] 문제 {len(user_data.problems)}개, 스트릭 {len(baekjoon_account.streaks)}개 기록")

        # 6. 저장
        saved_account = await self.baekjoon_account_repository.save(baekjoon_account)
        
        await self.domain_event_bus.publish(event)