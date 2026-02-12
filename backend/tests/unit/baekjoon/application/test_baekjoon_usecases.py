import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId, TierId
from app.core.exception import APIException


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
