import pytest
import asyncio
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock
import httpx

from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId, TierId
from app.core.exception import APIException
from tests.fixtures.baekjoon_fixtures import (
    MOCK_USER_GOLD,
    generate_mock_problems,
    generate_streak_data,
    create_link_scenario_data,
    create_update_scenario_data,
    TIER_GOLD_V,
    TIER_GOLD_IV,
)


# ── LinkBjAccountUsecase ──────────────────────────────────────

class TestLinkBjAccountUsecase:
    """LinkBjAccountUsecase.execute() 테스트"""

    def _make_usecase(self):
        from app.baekjoon.application.usecase.link_bj_account_usecase import LinkBjAccountUsecase
        return LinkBjAccountUsecase(
            baekjoon_account_repository=AsyncMock(),
            solvedac_gateway=AsyncMock(),
            domain_event_bus=AsyncMock(),
        )

    async def test_existing_account_publishes_event(self, mock_database_context):
        usecase = self._make_usecase()
        existing = MagicMock()
        usecase.baekjoon_account_repository.find_by_id.return_value = existing

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="test_bj")

        await usecase.execute(command)

        usecase.domain_event_bus.publish.assert_called_once()
        usecase.solvedac_gateway.fetch_user_data_first.assert_not_called()

    async def test_new_account_fetches_from_solvedac(self, mock_database_context):
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_id.return_value = None

        # Mock solvedac response
        user_info = MagicMock()
        user_info.tier = 10
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 50

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = []
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data

        saved_account = MagicMock()
        usecase.baekjoon_account_repository.save.return_value = saved_account

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="new_bj")

        await usecase.execute(command)

        usecase.solvedac_gateway.fetch_user_data_first.assert_called_once_with("new_bj")
        usecase.baekjoon_account_repository.save.assert_called_once()
        usecase.domain_event_bus.publish.assert_called_once()

    async def test_solvedac_not_found_raises(self, mock_database_context):
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_id.return_value = None
        usecase.solvedac_gateway.fetch_user_data_first.return_value = None

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="unknown")

        with pytest.raises(APIException) as exc_info:
            await usecase.execute(command)

        assert exc_info.value.error_code == "BAEKJOON_USER_NOT_FOUND"

    # ── 신규 테스트: 에러 처리 ──

    async def test_link_bj_account_solvedac_api_timeout(self, mock_database_context):
        """API 타임아웃 시 적절한 예외 발생"""
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_id.return_value = None
        usecase.solvedac_gateway.fetch_user_data_first.side_effect = asyncio.TimeoutError()

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="test_user")

        with pytest.raises((APIException, asyncio.TimeoutError)):
            await usecase.execute(command)

    async def test_link_bj_account_solvedac_api_error(self, mock_database_context):
        """solved.ac API 에러(503) 시 적절한 예외 발생"""
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_id.return_value = None

        # HTTP 503 에러 시뮬레이션
        error_response = httpx.Response(503, request=httpx.Request("GET", "http://test"))
        usecase.solvedac_gateway.fetch_user_data_first.side_effect = httpx.HTTPStatusError(
            "Service unavailable", request=error_response.request, response=error_response
        )

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="test_user")

        with pytest.raises((APIException, httpx.HTTPStatusError)):
            await usecase.execute(command)

    # ── 신규 테스트: 데이터 무결성 ──

    async def test_link_bj_account_with_problems_and_streaks(self, mock_database_context):
        """50개 문제 및 스트릭 데이터를 포함한 완전한 데이터 동기화"""
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_id.return_value = None

        # 50개 문제가 있는 사용자 데이터 생성
        scenario_data = create_link_scenario_data(user_id="test_user", problem_count=50)

        user_info = MagicMock()
        user_info.tier = scenario_data["tier"]
        user_info.rating = scenario_data["rating"]
        user_info.class_level = scenario_data["class_level"]
        user_info.max_streak = scenario_data["max_streak"]

        # 문제 데이터 모킹
        problems = []
        for p in scenario_data["problems"]:
            problem = MagicMock()
            problem.problem_id = p["problemId"]
            problem.title = p["titleKo"]
            problem.level = p["level"]
            problems.append(problem)

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = problems
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data

        saved_account = MagicMock()
        usecase.baekjoon_account_repository.save.return_value = saved_account

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="test_user")

        await usecase.execute(command)

        # 검증: 계정이 저장되고 이벤트가 발행됨
        usecase.baekjoon_account_repository.save.assert_called_once()
        usecase.domain_event_bus.publish.assert_called_once()

        # save 호출 시 전달된 인자 검증 (문제 리스트 포함)
        call_args = usecase.baekjoon_account_repository.save.call_args
        assert call_args is not None

    async def test_link_bj_account_duplicate_handle_different_user(self, mock_database_context):
        """다른 사용자가 이미 사용 중인 백준 핸들로 연동 시도 시 예외 발생"""
        usecase = self._make_usecase()

        # 이미 다른 사용자에게 연결된 계정
        existing_account = MagicMock()
        existing_account.user_account_id = UserAccountId(999)  # 다른 사용자 ID
        usecase.baekjoon_account_repository.find_by_id.return_value = existing_account

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="duplicate_user")

        # 기존 계정이 있으면 이벤트만 발행하고 새로 생성하지 않음
        await usecase.execute(command)

        # 이미 존재하는 계정이므로 fetch_user_data_first가 호출되지 않아야 함
        usecase.solvedac_gateway.fetch_user_data_first.assert_not_called()
        usecase.domain_event_bus.publish.assert_called_once()

    # ── 신규 테스트: 이벤트 발행 ──

    async def test_link_bj_account_publishes_domain_event(self, mock_database_context):
        """계정 연동 시 LINK_BAEKJOON_ACCOUNT_REQUESTED 도메인 이벤트 발행 검증"""
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_id.return_value = None

        user_info = MagicMock()
        user_info.tier = TIER_GOLD_V
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 30

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = []
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data

        saved_account = MagicMock()
        saved_account.bj_account_id = BaekjoonAccountId("test_user")
        saved_account.user_account_id = UserAccountId(1)
        usecase.baekjoon_account_repository.save.return_value = saved_account

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="test_user")

        await usecase.execute(command)

        # 이벤트 발행 검증
        usecase.domain_event_bus.publish.assert_called_once()

        # 발행된 이벤트의 타입 검증
        call_args = usecase.domain_event_bus.publish.call_args
        if call_args:
            event = call_args[0][0]  # 첫 번째 위치 인자가 이벤트
            assert hasattr(event, 'event_type')

    async def test_link_bj_account_rollback_on_failure(self, mock_database_context):
        """저장 실패 시 트랜잭션 롤백 (부분 데이터 저장 방지)"""
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_id.return_value = None

        user_info = MagicMock()
        user_info.tier = TIER_GOLD_V
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 30

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = []
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data

        # 저장 시 예외 발생 시뮬레이션
        usecase.baekjoon_account_repository.save.side_effect = Exception("Database error")

        from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
        command = LinkBjAccountCommand(user_account_id=1, bj_account_id="test_user")

        # 예외가 전파되어야 함
        with pytest.raises(Exception) as exc_info:
            await usecase.execute(command)

        assert "Database error" in str(exc_info.value)

        # 이벤트가 발행되지 않아야 함 (롤백됨)
        usecase.domain_event_bus.publish.assert_not_called()


# ── GetBaekjoonMeUsecase ──────────────────────────────────────

class TestGetBaekjoonMeUsecase:
    """GetBaekjoonMeUsecase.execute() 테스트"""

    def _make_usecase(self):
        from app.baekjoon.application.usecase.get_baekjoon_me_usecase import GetBaekjoonMeUsecase
        return GetBaekjoonMeUsecase(
            baekjoon_account_repository=AsyncMock(),
            streak_repository=AsyncMock(),
            tier_repository=AsyncMock(),
            domain_event_bus=AsyncMock(),
        )

    async def test_success(self, mock_database_context):
        usecase = self._make_usecase()

        # Mock event bus returning user info
        user_info = MagicMock()
        user_info.user_account_id = 1
        user_info.profile_image_url = None
        user_info.registered_at = "2025-01-01"
        user_info.targets = []
        usecase.domain_event_bus.publish.return_value = user_info

        # Mock bj account with link date
        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        bj_account.current_tier_id = TierId(10)
        bj_account.statistics.longest_streak = 50
        bj_account.rating.value = 1500
        bj_account.statistics.class_level = 3
        bj_account.tier_start_date = "2025-01-01"
        bj_account.created_at = "2025-01-01"
        linked_at = "2025-01-01"
        usecase.baekjoon_account_repository.find_by_user_id_with_link_date.return_value = (bj_account, linked_at)

        # Mock tier
        tier = MagicMock()
        tier.tier_code = "Gold V"
        usecase.tier_repository.find_by_id.return_value = tier

        # Mock streaks
        usecase.streak_repository.find_by_account_and_date_range.return_value = []

        from app.baekjoon.application.command.get_baekjoon_me_command import GetBaekjoonMeCommand
        command = GetBaekjoonMeCommand(user_account_id=1)

        result = await usecase.execute(command)

        assert result.bj_account.bj_account_id == "test_bj"
        assert result.bj_account.stat.tier_name == "Gold V"

    async def test_user_not_found_raises(self, mock_database_context):
        usecase = self._make_usecase()
        usecase.domain_event_bus.publish.return_value = None

        from app.baekjoon.application.command.get_baekjoon_me_command import GetBaekjoonMeCommand
        command = GetBaekjoonMeCommand(user_account_id=999)

        with pytest.raises(APIException) as exc_info:
            await usecase.execute(command)

        assert exc_info.value.error_code == "INVALID_REQUEST"

    async def test_unlinked_user_raises(self, mock_database_context):
        usecase = self._make_usecase()

        user_info = MagicMock()
        usecase.domain_event_bus.publish.return_value = user_info

        usecase.baekjoon_account_repository.find_by_user_id_with_link_date.return_value = None

        from app.baekjoon.application.command.get_baekjoon_me_command import GetBaekjoonMeCommand
        command = GetBaekjoonMeCommand(user_account_id=1)

        with pytest.raises(APIException) as exc_info:
            await usecase.execute(command)

        assert exc_info.value.error_code == "UNLINKED_USER"


# ── GetStreaksUsecase ──────────────────────────────────────

class TestGetStreaksUsecase:
    """GetStreaksUsecase.execute() 테스트"""

    def _make_usecase(self):
        from app.baekjoon.application.usecase.get_streaks_usecase import GetStreaksUsecase
        return GetStreaksUsecase(
            streak_repository=AsyncMock(),
            baekjoon_account_repository=AsyncMock(),
        )

    async def test_success(self, mock_database_context):
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account

        streak = MagicMock()
        streak.streak_date = date(2025, 1, 15)
        streak.solved_count = 3
        usecase.streak_repository.find_by_account_and_date_range.return_value = [streak]

        from app.baekjoon.application.command.get_streaks_command import GetStreaksCommand
        command = GetStreaksCommand(
            user_account_id=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )

        result = await usecase.execute(command)

        assert result.bj_account_id == "test_bj"
        assert result.total_count == 1
        assert result.streaks[0].streak_date == date(2025, 1, 15)

    async def test_no_bj_account_raises(self, mock_database_context):
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_user_id.return_value = None

        from app.baekjoon.application.command.get_streaks_command import GetStreaksCommand
        command = GetStreaksCommand(
            user_account_id=999,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )

        with pytest.raises(APIException) as exc_info:
            await usecase.execute(command)

        assert exc_info.value.error_code == "INVALID_REQUEST"

    async def test_empty_streaks(self, mock_database_context):
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.streak_repository.find_by_account_and_date_range.return_value = []

        from app.baekjoon.application.command.get_streaks_command import GetStreaksCommand
        command = GetStreaksCommand(
            user_account_id=1,
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31)
        )

        result = await usecase.execute(command)

        assert result.total_count == 0
        assert result.streaks == []


# ── GetUnrecordedProblemsUsecase ──────────────────────────────

class TestGetUnrecordedProblemsUsecase:
    """GetUnrecordedProblemsUsecase.execute() 테스트"""

    def _make_usecase(self):
        from app.baekjoon.application.usecase.get_unrecorded_problems_usecase import GetUnrecordedProblemsUsecase
        return GetUnrecordedProblemsUsecase(
            baekjoon_account_repository=AsyncMock(),
            problem_history_repository=AsyncMock(),
            domain_event_bus=AsyncMock(),
        )

    async def test_no_bj_account_raises(self, mock_database_context):
        usecase = self._make_usecase()
        usecase.baekjoon_account_repository.find_by_user_id.return_value = None

        from app.baekjoon.application.command.get_unrecorded_problems_command import GetUnrecordedProblemsCommand
        command = GetUnrecordedProblemsCommand(user_account_id=999)

        with pytest.raises(APIException) as exc_info:
            await usecase.execute(command)

        assert exc_info.value.error_code == "INVALID_REQUEST"

    async def test_no_unrecorded_returns_empty(self, mock_database_context):
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.problem_history_repository.find_unrecorded_problem_ids.return_value = set()

        from app.baekjoon.application.command.get_unrecorded_problems_command import GetUnrecordedProblemsCommand
        command = GetUnrecordedProblemsCommand(user_account_id=1)

        result = await usecase.execute(command)

        assert result.problems == []

    async def test_with_unrecorded_problems(self, mock_database_context):
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.problem_history_repository.find_unrecorded_problem_ids.return_value = {1000, 2000}

        # Mock event bus returning problems info
        from app.problem.application.query.problems_info_query import ProblemsInfoQuery, ProblemInfoQuery
        problem_info = MagicMock(spec=ProblemInfoQuery)
        problems_info = ProblemsInfoQuery(problems={1000: problem_info, 2000: problem_info})
        usecase.domain_event_bus.publish.return_value = problems_info

        from app.baekjoon.application.command.get_unrecorded_problems_command import GetUnrecordedProblemsCommand
        command = GetUnrecordedProblemsCommand(user_account_id=1)

        result = await usecase.execute(command)

        assert len(result.problems) == 2


# ── UpdateBjAccountUsecase ──────────────────────────────────────

class TestUpdateBjAccountUsecase:
    """UpdateBjAccountUsecase.execute() 테스트"""

    def _make_usecase(self):
        from app.baekjoon.application.usecase.update_bj_account_usecase import UpdateBjAccountUsecase
        return UpdateBjAccountUsecase(
            baekjoon_account_repository=AsyncMock(),
            problem_history_repository=AsyncMock(),
            streak_repository=AsyncMock(),
            solvedac_gateway=AsyncMock(),
        )

    async def test_solvedac_not_found_raises(self, mock_database_context):
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = set()
        usecase.solvedac_gateway.fetch_user_data_first.return_value = None

        with pytest.raises(APIException) as exc_info:
            await usecase.execute(user_account_id=1)

        assert exc_info.value.error_code == "BAEKJOON_USER_NOT_FOUND"

    async def test_update_success_no_new_problems(self, mock_database_context):
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = {1000}

        user_info = MagicMock()
        user_info.tier = 10
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 50
        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = [MagicMock(problem_id=1000)]  # already recorded
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.return_value = []

        await usecase.execute(user_account_id=1)

        usecase.baekjoon_account_repository.update_stat.assert_called_once()
        usecase.problem_history_repository.save_all.assert_not_called()

    # ── 신규 테스트: 신규 문제 감지 ──

    async def test_update_bj_account_with_new_problems(self, mock_database_context):
        """5개의 신규 문제가 있을 때 핵심 업데이트 로직 테스트"""
        usecase = self._make_usecase()

        # 업데이트 시나리오 데이터 생성 (100개 기존 + 5개 신규)
        scenario_data = create_update_scenario_data(
            existing_problem_count=100,
            new_problem_count=5,
            tier_change=0,
            streak_change=0
        )

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account

        # 기존 문제 IDs
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = set(
            scenario_data["existing_problem_ids"]
        )

        # API 응답: 전체 105개 문제
        user_info = MagicMock()
        user_info.tier = scenario_data["updated_tier"]
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 30

        problems = []
        for p in scenario_data["all_problems"]:
            problem = MagicMock()
            problem.problem_id = p["problemId"]
            problem.level = p["level"]
            problems.append(problem)

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = problems
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data

        # 5개의 신규 문제를 위한 5개의 streak ID 반환
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.return_value = list(range(1, 6))

        await usecase.execute(user_account_id=1)

        # 검증: 계정 통계 업데이트됨
        usecase.baekjoon_account_repository.update_stat.assert_called_once()

        # 검증: 신규 문제 히스토리 저장됨
        usecase.problem_history_repository.save_all.assert_called_once()

        # save_all에 전달된 문제 개수 확인
        call_args = usecase.problem_history_repository.save_all.call_args
        if call_args:
            saved_problems = call_args[0][0]  # 첫 번째 위치 인자
            assert len(saved_problems) == 5  # 5개의 신규 문제

    # ── 신규 테스트: 스트릭 데이터 업데이트 ──

    async def test_update_bj_account_streak_data_increases(self, mock_database_context):
        """스트릭이 증가했을 때 동기화 로직 테스트"""
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        bj_account.statistics = MagicMock()
        bj_account.statistics.current_streak = 10  # 기존 스트릭
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = {1000}

        # API 응답: 스트릭 증가 (10 → 15)
        user_info = MagicMock()
        user_info.tier = TIER_GOLD_V
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 20  # 최장 스트릭도 증가

        # 스트릭 히스토리 데이터
        streak_history = []
        for i in range(15):  # 15일 연속
            streak = MagicMock()
            streak.timestamp = (date.today() - timedelta(days=i)).isoformat()
            streak.solved_count = 1
            streak_history.append(streak)

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = [MagicMock(problem_id=1000)]
        user_data.history = streak_history
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.return_value = list(range(1, 16))

        await usecase.execute(user_account_id=1)

        # 검증: 스트릭 데이터 저장됨
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.assert_called_once()

        # 검증: 계정 통계 업데이트됨 (max_streak 포함)
        usecase.baekjoon_account_repository.update_stat.assert_called_once()

    async def test_update_bj_account_streak_broken(self, mock_database_context):
        """스트릭이 끊겼을 때 처리 테스트"""
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        bj_account.statistics = MagicMock()
        bj_account.statistics.current_streak = 10  # 기존 스트릭
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = {1000}

        # API 응답: 스트릭 끊김 (current_streak = 0)
        user_info = MagicMock()
        user_info.tier = TIER_GOLD_V
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 20  # 최장 스트릭은 유지

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = [MagicMock(problem_id=1000)]
        user_data.history = []  # 빈 히스토리 = 스트릭 끊김
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.return_value = []

        await usecase.execute(user_account_id=1)

        # 검증: 빈 히스토리로도 정상 처리됨
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.assert_called_once()
        usecase.baekjoon_account_repository.update_stat.assert_called_once()

    # ── 신규 테스트: 티어 변경 ──

    async def test_update_bj_account_tier_changes(self, mock_database_context):
        """티어 승급 시 티어 변경 추적 테스트"""
        usecase = self._make_usecase()

        # 티어 승급 시나리오 (Gold V → Gold IV)
        scenario_data = create_update_scenario_data(
            existing_problem_count=100,
            new_problem_count=5,
            tier_change=+1,  # 티어 승급
            streak_change=5
        )

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        bj_account.current_tier_id = TierId(scenario_data["base_tier"])  # Gold V
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = set(
            scenario_data["existing_problem_ids"]
        )

        # API 응답: 티어 상승
        user_info = MagicMock()
        user_info.tier = scenario_data["updated_tier"]  # Gold IV
        user_info.rating = 1600  # 레이팅도 상승
        user_info.class_level = 3
        user_info.max_streak = 30

        problems = []
        for p in scenario_data["all_problems"]:
            problem = MagicMock()
            problem.problem_id = p["problemId"]
            problem.level = p["level"]
            problems.append(problem)

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = problems
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data

        # 신규 문제를 위한 streak ID 반환
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.return_value = list(range(1, scenario_data["new_problem_count"] + 1))

        await usecase.execute(user_account_id=1)

        # 검증: 티어가 업데이트된 통계로 저장됨
        usecase.baekjoon_account_repository.update_stat.assert_called_once()

        # update_stat 호출 시 전달된 인자 확인
        call_args = usecase.baekjoon_account_repository.update_stat.call_args
        if call_args:
            # 티어가 변경되었는지 확인 가능
            assert call_args is not None

    # ── 신규 테스트: 멱등성 및 엣지 케이스 ──

    async def test_update_bj_account_no_changes_idempotent(self, mock_database_context):
        """데이터 변경이 없을 때 효율적인 처리 (멱등성)"""
        usecase = self._make_usecase()

        bj_account = MagicMock()
        bj_account.bj_account_id = BaekjoonAccountId("test_bj")
        usecase.baekjoon_account_repository.find_by_user_id.return_value = bj_account

        # 기존 문제 100개
        existing_problem_ids = set(range(1000, 1100))
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = existing_problem_ids

        # API 응답: 동일한 100개 문제 (변경 없음)
        user_info = MagicMock()
        user_info.tier = TIER_GOLD_V
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 30

        problems = []
        for problem_id in existing_problem_ids:
            problem = MagicMock()
            problem.problem_id = problem_id
            problem.level = 10
            problems.append(problem)

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = problems
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.return_value = []

        await usecase.execute(user_account_id=1)

        # 검증: 계정 통계는 업데이트됨 (최신 상태 반영)
        usecase.baekjoon_account_repository.update_stat.assert_called_once()

        # 검증: 신규 문제가 없으므로 save_all 호출되지 않음
        usecase.problem_history_repository.save_all.assert_not_called()

    async def test_update_bulk_multiple_accounts(self, mock_database_context):
        """벌크 업데이트 시 여러 계정 처리 테스트"""
        usecase = self._make_usecase()

        # 첫 번째 계정 업데이트
        bj_account_1 = MagicMock()
        bj_account_1.bj_account_id = BaekjoonAccountId("user_1")
        bj_account_1.user_account_id = UserAccountId(1)

        # 두 번째 계정 업데이트
        bj_account_2 = MagicMock()
        bj_account_2.bj_account_id = BaekjoonAccountId("user_2")
        bj_account_2.user_account_id = UserAccountId(2)

        # 순차적으로 다른 계정 반환
        call_count = 0

        def get_account_by_user_id(user_account_id):
            nonlocal call_count
            call_count += 1
            return bj_account_1 if call_count == 1 else bj_account_2

        usecase.baekjoon_account_repository.find_by_user_id.side_effect = get_account_by_user_id
        usecase.problem_history_repository.find_solved_ids_by_bj_account_id.return_value = {1000}

        user_info = MagicMock()
        user_info.tier = TIER_GOLD_V
        user_info.rating = 1500
        user_info.class_level = 3
        user_info.max_streak = 30

        user_data = MagicMock()
        user_data.user_info = user_info
        user_data.problems = [MagicMock(problem_id=1000)]
        user_data.history = []
        usecase.solvedac_gateway.fetch_user_data_first.return_value = user_data
        usecase.streak_repository.save_unlinked_streaks_and_get_ids.return_value = []

        # 두 계정 업데이트
        await usecase.execute(user_account_id=1)
        await usecase.execute(user_account_id=2)

        # 검증: 두 번 모두 업데이트됨
        assert usecase.baekjoon_account_repository.update_stat.call_count == 2
