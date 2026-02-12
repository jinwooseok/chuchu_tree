import pytest
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.vo.current_user import CurrentUser
from app.core.api_response import ApiResponse
from app.user.presentation.controller.user_controller import (
    set_profile_image,
    delete_profile_image,
    get_user_tags,
    get_user_targets,
    update_user_target,
    get_all_user_accounts,
)


@pytest.fixture
def mock_current_user():
    return CurrentUser(user_account_id=1)


@pytest.fixture
def mock_user_service():
    return AsyncMock()


@pytest.fixture
def mock_user_tags_usecase():
    return AsyncMock()


class TestUserController:
    """User Controller 단위 테스트 - 함수 직접 호출"""

    async def test_set_profile_image_returns_api_response(self, mock_current_user):
        mock_file = MagicMock()
        result = await set_profile_image(
            profile_image=mock_file,
            current_user=mock_current_user,
        )
        assert isinstance(result, ApiResponse)

    async def test_delete_profile_image_returns_api_response(self, mock_current_user):
        result = await delete_profile_image(current_user=mock_current_user)
        assert isinstance(result, ApiResponse)

    async def test_get_user_tags_calls_usecase(self, mock_current_user, mock_user_tags_usecase):
        mock_query = MagicMock()
        mock_user_tags_usecase.execute.return_value = mock_query

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {}

        from app.user.presentation.schema.response.user_tag_response import UserTagsResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(UserTagsResponse, "from_query", lambda q: mock_response)
            result = await get_user_tags(
                current_user=mock_current_user,
                usecase=mock_user_tags_usecase,
            )

        mock_user_tags_usecase.execute.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_get_user_targets_calls_service(self, mock_current_user, mock_user_service):
        mock_query = MagicMock()
        mock_user_service.get_user_target.return_value = mock_query

        mock_response = MagicMock()
        mock_response.model_dump.return_value = {}

        from app.user.presentation.schema.response.user_tag_response import TargetResponse
        with pytest.MonkeyPatch.context() as m:
            m.setattr(TargetResponse, "from_query", lambda q: mock_response)
            result = await get_user_targets(
                current_user=mock_current_user,
                user_account_application_service=mock_user_service,
            )

        mock_user_service.get_user_target.assert_called_once_with(1)
        assert isinstance(result, ApiResponse)

    async def test_update_user_target_calls_service(self, mock_current_user, mock_user_service):
        mock_user_service.update_user_target.return_value = None

        from app.user.presentation.schema.request.user_target_request import UpdateUserTargetRequest
        request = UpdateUserTargetRequest(targetCode="COTE")

        result = await update_user_target(
            request=request,
            current_user=mock_current_user,
            user_account_application_service=mock_user_service,
        )

        mock_user_service.update_user_target.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_get_all_user_accounts_returns_api_response(self, mock_current_user):
        result = await get_all_user_accounts(
            page=1,
            current_user=mock_current_user,
        )
        assert isinstance(result, ApiResponse)
