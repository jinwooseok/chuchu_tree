import pytest
from unittest.mock import AsyncMock, MagicMock

from fastapi import Request, Response
from fastapi.responses import RedirectResponse

from app.common.domain.vo.current_user import CurrentUser
from app.core.api_response import ApiResponse
from app.common.presentation.controller.auth_controller import (
    me,
    logout,
    refresh_token,
    social_login,
    handle_social_login_callback,
    get_withdraw_url,
)


@pytest.fixture
def mock_auth_service():
    return AsyncMock()


@pytest.fixture
def mock_current_user():
    return CurrentUser(user_account_id=1)


@pytest.fixture
def mock_request():
    """FastAPI Request mock"""
    scope = {"type": "http", "method": "GET", "headers": []}
    return Request(scope)


@pytest.fixture
def mock_response():
    """FastAPI Response mock"""
    resp = Response()
    return resp


class TestAuthController:
    """Auth Controller 단위 테스트 - 함수 직접 호출"""

    async def test_me_returns_api_response(self, mock_current_user):
        result = await me(current_user=mock_current_user)
        assert isinstance(result, ApiResponse)

    async def test_logout_calls_service(self, mock_auth_service, mock_current_user, mock_request, mock_response):
        mock_auth_service.logout.return_value = None

        result = await logout(
            request=mock_request,
            response=mock_response,
            current_user=mock_current_user,
            auth_application_service=mock_auth_service,
        )

        assert isinstance(result, ApiResponse)

    async def test_refresh_token_calls_service(self, mock_auth_service):
        mock_auth_service.refresh_access_token.return_value = None

        result = await refresh_token(
            refresh_token="test_refresh_token",
            auth_application_service=mock_auth_service,
        )

        mock_auth_service.refresh_access_token.assert_called_once()
        assert isinstance(result, ApiResponse)

    async def test_social_login_returns_redirect(self, mock_auth_service):
        mock_auth_service.get_social_login_url.return_value = "https://kakao.com/login"

        result = await social_login(
            provider="kakao",
            frontend_redirect_url=None,
            auth_application_service=mock_auth_service,
        )

        assert isinstance(result, RedirectResponse)
        assert result.status_code == 302

    async def test_social_login_callback_returns_redirect(self, mock_auth_service, mock_request, mock_response):
        mock_auth_service.handle_social_login_callback.return_value = "https://frontend.com/success"

        result = await handle_social_login_callback(
            request=mock_request,
            response=mock_response,
            provider="kakao",
            code="test_code",
            state="test_state",
            auth_application_service=mock_auth_service,
        )

        assert isinstance(result, RedirectResponse)
        assert result.status_code == 302

    async def test_withdraw_returns_redirect(self, mock_auth_service, mock_current_user, mock_request):
        mock_auth_service.get_withdraw_url.return_value = "https://kakao.com/withdraw"

        result = await get_withdraw_url(
            request=mock_request,
            frontend_redirect_url=None,
            current_user=mock_current_user,
            auth_application_service=mock_auth_service,
        )

        assert isinstance(result, RedirectResponse)
        assert result.status_code == 302
