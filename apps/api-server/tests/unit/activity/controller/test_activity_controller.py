import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.vo.current_user import CurrentUser
from app.core.api_response import ApiResponse
from app.activity.presentation.controller.activity_controller import (
    update_will_solve_problems,
    update_solved_problems,
    update_solved_and_will_solve_problems,
    batch_create_solved_problems,
    ban_problem,
    unban_problem,
    ban_tag,
    unban_tag,
    get_banned_problems,
    get_banned_tags,
    set_problem_representative_tag,
    get_problem_record,
    create_or_update_problem_record,
)


@pytest.fixture
def mock_activity_service():
    return AsyncMock()


@pytest.fixture
def mock_current_user():
    return CurrentUser(user_account_id=1)


class TestActivityController:
    """Activity Controller 단위 테스트 - 함수 직접 호출"""

    async def test_update_will_solve_problems_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.update_will_solve_problems.return_value = None

        from app.activity.presentation.schema.request.activity_request import UpdateWillSolveProblemsRequest
        request = UpdateWillSolveProblemsRequest(date=date(2025, 1, 15), problem_ids=[1000, 2000])

        result = await update_will_solve_problems(
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.update_will_solve_problems.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_update_solved_problems_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.update_solved_problems.return_value = None

        from app.activity.presentation.schema.request.activity_request import UpdateSolvedProblemsRequest
        request = UpdateSolvedProblemsRequest(date=date(2025, 1, 15), problem_ids=[1000])

        result = await update_solved_problems(
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.update_solved_problems.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_update_solved_and_will_solve_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.update_solved_and_will_solve_problems.return_value = None

        from app.activity.presentation.schema.request.activity_request import UpdateSolvedAndWillSolveProblemsRequest
        request = UpdateSolvedAndWillSolveProblemsRequest(
            date=date(2025, 1, 15),
            solved_problem_ids=[1000],
            will_solve_problem_ids=[2000],
        )

        result = await update_solved_and_will_solve_problems(
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.update_solved_and_will_solve_problems.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_batch_create_solved_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.batch_create_solved_problems.return_value = None

        from app.activity.presentation.schema.request.activity_request import SolvedProblemBatchItem
        request = [SolvedProblemBatchItem(date=date(2025, 1, 15), problem_ids=[1000])]

        result = await batch_create_solved_problems(
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.batch_create_solved_problems.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_ban_problem_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.ban_problem.return_value = None

        from app.activity.presentation.schema.request.activity_request import BanProblemRequest
        request = BanProblemRequest(problem_id=1000)

        result = await ban_problem(
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.ban_problem.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_unban_problem_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.unban_problem.return_value = None

        result = await unban_problem(
            problem_id=1000,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.unban_problem.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_ban_tag_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.ban_tag.return_value = None

        from app.activity.presentation.schema.request.activity_request import BanTagRequest
        request = BanTagRequest(tag_code="dp")

        result = await ban_tag(
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.ban_tag.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_unban_tag_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.unban_tag.return_value = None

        result = await unban_tag(
            tag_code="dp",
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.unban_tag.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_get_banned_problems_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_query = MagicMock()
        mock_activity_service.get_banned_problems.return_value = mock_query

        from app.activity.presentation.schema.response.activity_response import BannedProblemsResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(BannedProblemsResponse, "from_query", lambda q: {})
            result = await get_banned_problems(
                current_user=mock_current_user,
                activity_application_service=mock_activity_service,
            )

        mock_activity_service.get_banned_problems.assert_called_once_with(1)
        assert isinstance(result, ApiResponse)

    async def test_get_banned_tags_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_query = MagicMock()
        mock_activity_service.get_banned_tags.return_value = mock_query

        from app.activity.presentation.schema.response.activity_response import BannedTagsResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(BannedTagsResponse, "from_query", lambda q: {})
            result = await get_banned_tags(
                current_user=mock_current_user,
                activity_application_service=mock_activity_service,
            )

        mock_activity_service.get_banned_tags.assert_called_once_with(1)
        assert isinstance(result, ApiResponse)

    async def test_set_representative_tag_calls_service(
        self, mock_current_user, mock_activity_service
    ):
        mock_activity_service.set_problem_representative_tag.return_value = None

        from app.activity.presentation.schema.request.activity_request import SetRepresentativeTagRequest
        request = SetRepresentativeTagRequest(representative_tag_code="dp")

        result = await set_problem_representative_tag(
            problem_id=1000,
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )

        mock_activity_service.set_problem_representative_tag.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_get_problem_record_returns_api_response(self, mock_current_user):
        result = await get_problem_record(
            problem_id=1000,
            current_user=mock_current_user,
        )
        assert isinstance(result, ApiResponse)

    async def test_create_problem_record_returns_api_response(
        self, mock_current_user, mock_activity_service
    ):
        from app.activity.presentation.schema.request.activity_request import ProblemRecordRequest
        request = ProblemRecordRequest(problem_id=1000, memo_title="test", content="body")

        result = await create_or_update_problem_record(
            request=request,
            current_user=mock_current_user,
            activity_application_service=mock_activity_service,
        )
        assert isinstance(result, ApiResponse)
