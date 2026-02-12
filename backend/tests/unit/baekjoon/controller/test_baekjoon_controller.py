import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.vo.current_user import CurrentUser
from app.core.api_response import ApiResponse
from app.baekjoon.presentation.controller.baekjoon_controller import (
    link_baekjoon_account,
    update_baekjoon_account_link,
    get_baekjoon_me,
    get_baekjoon_streak,
    refresh_problem_data,
    get_unrecorded_problems_me,
)


@pytest.fixture
def mock_current_user():
    return CurrentUser(user_account_id=1)


@pytest.fixture
def mock_usecases():
    return {
        "link": AsyncMock(),
        "me": AsyncMock(),
        "streaks": AsyncMock(),
        "update": AsyncMock(),
        "unrecorded": AsyncMock(),
    }


class TestBaekjoonController:
    """Baekjoon Controller 단위 테스트 - 함수 직접 호출"""

    async def test_link_account_calls_usecase(self, mock_current_user, mock_usecases):
        mock_usecases["link"].execute.return_value = None

        from app.baekjoon.presentation.schema.request.baekjoon_request import LinkBaekjoonAccountRequest
        request = LinkBaekjoonAccountRequest(bjAccount="test_bj")

        result = await link_baekjoon_account(
            request=request,
            current_user=mock_current_user,
            link_bj_account_usecase=mock_usecases["link"],
        )

        mock_usecases["link"].execute.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_update_link_calls_usecase(self, mock_current_user, mock_usecases):
        mock_usecases["link"].execute.return_value = None

        from app.baekjoon.presentation.schema.request.baekjoon_request import LinkBaekjoonAccountRequest
        request = LinkBaekjoonAccountRequest(bjAccount="new_bj")

        result = await update_baekjoon_account_link(
            request=request,
            current_user=mock_current_user,
            link_bj_account_usecase=mock_usecases["link"],
        )

        mock_usecases["link"].execute.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_get_me_calls_usecase(self, mock_current_user, mock_usecases):
        mock_query = MagicMock()
        mock_usecases["me"].execute.return_value = mock_query

        from app.baekjoon.presentation.schema.response.get_baekjoon_me_response import GetBaekjoonMeResponse
        with pytest.MonkeyPatch.context() as m:
            # ApiResponse(data=response_data) 에서 Pydantic 모델을 직접 넘기므로
            # from_query가 dict를 반환해야 직렬화 가능
            m.setattr(GetBaekjoonMeResponse, "from_query", lambda q: {})
            result = await get_baekjoon_me(
                current_user=mock_current_user,
                get_baekjoon_me_usecase=mock_usecases["me"],
            )

        mock_usecases["me"].execute.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_get_streak_calls_usecase(self, mock_current_user, mock_usecases):
        mock_query = MagicMock()
        mock_usecases["streaks"].execute.return_value = mock_query

        from app.baekjoon.presentation.schema.response.get_streaks_response import GetStreaksResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(GetStreaksResponse, "from_query", lambda q: {})
            result = await get_baekjoon_streak(
                start_date=date(2025, 1, 1),
                end_date=date(2025, 1, 31),
                current_user=mock_current_user,
                get_streaks_usecase=mock_usecases["streaks"],
            )

        mock_usecases["streaks"].execute.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_refresh_calls_usecase(self, mock_current_user, mock_usecases):
        mock_usecases["update"].execute.return_value = None

        result = await refresh_problem_data(
            current_user=mock_current_user,
            update_bj_account_usecase=mock_usecases["update"],
        )

        mock_usecases["update"].execute.assert_called_once_with(1)
        assert isinstance(result, ApiResponse)

    async def test_get_unrecorded_calls_usecase(self, mock_current_user, mock_usecases):
        from app.baekjoon.application.query.get_unrecorded_problems_query import GetUnrecordedProblemsQuery
        mock_usecases["unrecorded"].execute.return_value = GetUnrecordedProblemsQuery(problems=[])

        from app.baekjoon.presentation.schema.response.get_unrecorded_problems_response import GetUnrecordedProblemsResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(GetUnrecordedProblemsResponse, "from_query", lambda q: {})
            result = await get_unrecorded_problems_me(
                current_user=mock_current_user,
                get_unrecorded_problems_usecase=mock_usecases["unrecorded"],
            )

        mock_usecases["unrecorded"].execute.assert_called_once()
        assert isinstance(result, ApiResponse)
