import pytest
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.vo.current_user import CurrentUser
from app.core.api_response import ApiResponse
from app.recommendation.presentation.controller.recommendation_controller import (
    get_recommended_problems,
)


@pytest.fixture
def mock_current_user():
    return CurrentUser(user_account_id=1)


@pytest.fixture
def mock_recommendation_usecase():
    return AsyncMock()


class TestRecommendationController:
    """Recommendation Controller 단위 테스트 - 함수 직접 호출"""

    async def test_get_recommended_problems_calls_usecase(
        self, mock_current_user, mock_recommendation_usecase
    ):
        mock_query = MagicMock()
        mock_recommendation_usecase.execute.return_value = mock_query

        from app.recommendation.presentation.schema.response.recommendation_response import RecommendationResponse
        with pytest.MonkeyPatch.context() as m:
            # ApiResponse(data=response_data) 에서 Pydantic 모델을 직접 넘기므로
            # from_query가 dict를 반환해야 직렬화 가능
            m.setattr(RecommendationResponse, "from_query", lambda q: {})
            result = await get_recommended_problems(
                level="[]",
                tags="[]",
                count=3,
                exclusion_mode="LENIENT",
                current_user=mock_current_user,
                recommendation_usecase=mock_recommendation_usecase,
            )

        mock_recommendation_usecase.execute.assert_called_once()
        assert isinstance(result, ApiResponse)
