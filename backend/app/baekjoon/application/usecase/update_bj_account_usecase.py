from datetime import datetime
from fastapi import logger
from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.baekjoon.domain.gateway.solvedac_gateway import SolvedacGateway
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.infra.repository.problem_history_repository_impl import ProblemHistoryRepositoryImpl
from app.common.domain.vo.identifiers import BaekjoonAccountId, ProblemId, TierId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


class UpdateBjAccountUsecase:
    """
    백준 계정과 연동하는 시나리오

    1. 유저 id로 백준 id를 찾음
    2. 그 백준 id를 기준으로 업데이트 진행
    """

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        problem_history_repository: ProblemHistoryRepositoryImpl,
        solvedac_gateway: SolvedacGateway
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.solvedac_gateway = solvedac_gateway
        self.problem_history_repository = problem_history_repository

    @transactional
    async def execute(self, user_account_id: int) -> None:
        # 1. 기존 데이터 로드
        existing_account = await self.baekjoon_account_repository.find_by_user_id(UserAccountId(user_account_id))
        existing_problem_history_ids = await self.problem_history_repository.find_solved_ids_by_bj_account_id(existing_account.bj_account_id)
        
        # 2. solved.ac 데이터 수집
        user_data = await self.solvedac_gateway.fetch_user_data_first(existing_account.bj_account_id.value)
   
        if user_data is None:
            raise APIException(ErrorCode.BAEKJOON_USER_NOT_FOUND)

        # 3. 유저 기본 정보 및 통계 업데이트 (추가된 부분)
        # 기존 객체의 필드를 업데이트합니다.
        existing_account.update_tier(TierId(user_data.user_info.tier))
        existing_account.update_rating(user_data.user_info.rating)
        existing_account.update_statistics(
            contribution_count=0, # API 미제공 시
            class_level=user_data.user_info.class_level,
            longest_streak=user_data.user_info.max_streak
        )
        
        # 4. 새로운 문제 필터링
        new_problems = [p for p in user_data.problems if p.problem_id not in existing_problem_history_ids]
        
        # 6. 신규 문제 매칭
        if new_problems:
            # 어떤 날짜의 스트릭에 매칭할지 결정 (휴리스틱: API의 최신 날짜)
            latest_history = max(user_data.history, key=lambda x: x.timestamp)
            latest_date = datetime.fromisoformat(latest_history.timestamp.replace('Z', '+00:00')).date()
            
            for p in new_problems:
                # record_problem_solved는 streak_id 없이 문제 정보만 history에 추가
                # 단, 필요하다면 history 엔티티 내부에 solved_date 필드를 두어 나중에 매칭 포인트로 활용
                existing_account.record_problem_solved(
                    problem_id=ProblemId(p.problem_id),
                    solved_date=latest_date  # 이 날짜 정보가 매칭의 Key가 됨
                )

        await self.baekjoon_account_repository.update_stat(existing_account)
        
    @transactional
    async def execute_bulk(self) -> None:
        bj_account_ids: list[str] = self.baekjoon_account_repository.find_all_ids()
        for bj_account_id in bj_account_ids:
            self.execute(bj_account_id)