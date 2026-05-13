import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.api_response import ApiResponse
from app.problem.presentation.controller.problem_controller import search_problems


@pytest.fixture
def mock_problem_service():
    return AsyncMock()


class TestProblemController:
    """Problem Controller 단위 테스트 - 함수 직접 호출"""

    async def test_search_calls_service(self, mock_problem_service):
        mock_problem_service.search_problem_by_keyword.return_value = [[], []]

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {}

        from app.problem.presentation.schema.response.problem_response import ProblemSearchResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(ProblemSearchResponse, "from_queries", lambda a, b: mock_response)
            result = await search_problems(
                keyword="A+B",
                problem_application_service=mock_problem_service,
            )

        mock_problem_service.search_problem_by_keyword.assert_called_once_with("A+B")
        assert isinstance(result, ApiResponse)

    async def test_search_empty_keyword(self, mock_problem_service):
        mock_problem_service.search_problem_by_keyword.return_value = [[], []]

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {}

        from app.problem.presentation.schema.response.problem_response import ProblemSearchResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(ProblemSearchResponse, "from_queries", lambda a, b: mock_response)
            result = await search_problems(
                keyword="",
                problem_application_service=mock_problem_service,
            )

        mock_problem_service.search_problem_by_keyword.assert_called_once_with("")
        assert isinstance(result, ApiResponse)
