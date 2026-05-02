import pytest
from unittest.mock import AsyncMock, MagicMock

from app.core.api_response import ApiResponse
from app.target.presentation.controller.target_controller import get_all_targets


@pytest.fixture
def mock_target_service():
    return AsyncMock()


class TestTargetController:
    """Target Controller 단위 테스트 - 함수 직접 호출"""

    async def test_get_all_targets_calls_service(self, mock_target_service):
        mock_target_service.get_all_targets.return_value = []

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"targets": []}

        from app.target.presentation.schema.response.target_response import AllTargetsResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(AllTargetsResponse, "from_queries", lambda qs: mock_response)
            result = await get_all_targets(
                target_application_service=mock_target_service,
            )

        mock_target_service.get_all_targets.assert_called_once()
        assert isinstance(result, ApiResponse)
