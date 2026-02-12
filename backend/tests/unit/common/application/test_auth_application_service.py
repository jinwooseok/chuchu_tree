import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.common.application.command.social_login_command import SocialLoginCommand
from app.common.application.service.auth_application_service import AuthApplicationService
from app.common.domain.enums import Provider
from app.common.domain.vo.current_user import CurrentUser
from app.core.exception import APIException


class TestAuthenticateUser:
    """AuthApplicationService.authenticate_user() 테스트"""

    def _make_service(self, decode_return=None) -> AuthApplicationService:
        token_service = MagicMock()
        if decode_return is not None:
            token_service.decode_token.return_value = decode_return
        cookie_service = MagicMock()
        domain_event_bus = AsyncMock()

        return AuthApplicationService(
            token_service=token_service,
            cookie_service=cookie_service,
            kakao_oauth_client=AsyncMock(),
            naver_oauth_client=AsyncMock(),
            google_oauth_client=AsyncMock(),
            github_oauth_client=AsyncMock(),
            domain_event_bus=domain_event_bus,
        )

    def test_valid_token_returns_current_user(self):
        service = self._make_service(decode_return={"user_account_id": 42})

        result = service.authenticate_user("valid_token")

        assert isinstance(result, CurrentUser)
        assert result.user_account_id == 42

    def test_none_token_raises_no_login_status(self):
        service = self._make_service()

        with pytest.raises(APIException) as exc_info:
            service.authenticate_user(None)

        assert exc_info.value.error_code == "NO_LOGIN_STATUS"

    def test_empty_token_raises_no_login_status(self):
        service = self._make_service()

        with pytest.raises(APIException) as exc_info:
            service.authenticate_user("")

        assert exc_info.value.error_code == "NO_LOGIN_STATUS"

    def test_token_without_user_id_raises_authorization_failed(self):
        service = self._make_service(decode_return={})

        with pytest.raises(APIException) as exc_info:
            service.authenticate_user("some_token")

        assert exc_info.value.error_code == "AUTHORIZATION_FAILED"

    def test_expired_token_propagates_exception(self):
        service = self._make_service()
        service.token_service.decode_token.side_effect = APIException(
            __import__("app.core.error_codes", fromlist=["ErrorCode"]).ErrorCode.EXPIRED_TOKEN
        )

        with pytest.raises(APIException) as exc_info:
            service.authenticate_user("expired_token")

        assert exc_info.value.error_code == "EXPIRED_TOKEN"


class TestGetSocialLoginUrl:
    """AuthApplicationService.get_social_login_url() 테스트"""

    def _make_service(self) -> AuthApplicationService:
        kakao = AsyncMock()
        kakao.get_social_login_url = AsyncMock(return_value="https://kakao.com/login")
        naver = AsyncMock()
        naver.get_social_login_url = AsyncMock(return_value="https://naver.com/login")
        google = AsyncMock()
        google.get_social_login_url = AsyncMock(return_value="https://google.com/login")
        github = AsyncMock()
        github.get_social_login_url = AsyncMock(return_value="https://github.com/login")

        return AuthApplicationService(
            token_service=MagicMock(),
            cookie_service=MagicMock(),
            kakao_oauth_client=kakao,
            naver_oauth_client=naver,
            google_oauth_client=google,
            github_oauth_client=github,
            domain_event_bus=AsyncMock(),
        )

    async def test_kakao_login_url(self, mock_database_context):
        service = self._make_service()
        command = SocialLoginCommand(provider="KAKAO", frontend_redirect_url=None)

        result = await service.get_social_login_url(command)

        assert result == "https://kakao.com/login"

    async def test_naver_login_url(self, mock_database_context):
        service = self._make_service()
        command = SocialLoginCommand(provider="NAVER", frontend_redirect_url=None)

        result = await service.get_social_login_url(command)

        assert result == "https://naver.com/login"

    async def test_google_login_url(self, mock_database_context):
        service = self._make_service()
        command = SocialLoginCommand(provider="GOOGLE", frontend_redirect_url=None)

        result = await service.get_social_login_url(command)

        assert result == "https://google.com/login"

    async def test_github_login_url(self, mock_database_context):
        service = self._make_service()
        command = SocialLoginCommand(provider="GITHUB", frontend_redirect_url=None)

        result = await service.get_social_login_url(command)

        assert result == "https://github.com/login"

    async def test_invalid_provider_raises(self, mock_database_context):
        service = self._make_service()

        with pytest.raises(Exception):
            command = SocialLoginCommand(provider="INVALID", frontend_redirect_url=None)
            await service.get_social_login_url(command)


class TestLogout:
    """AuthApplicationService.logout() 테스트"""

    async def test_logout_clears_cookies(self, mock_database_context):
        cookie_service = MagicMock()
        service = AuthApplicationService(
            token_service=MagicMock(),
            cookie_service=cookie_service,
            kakao_oauth_client=AsyncMock(),
            naver_oauth_client=AsyncMock(),
            google_oauth_client=AsyncMock(),
            github_oauth_client=AsyncMock(),
            domain_event_bus=AsyncMock(),
        )

        response = MagicMock()
        await service.logout(response)

        assert cookie_service.delete_cookie.call_count == 2
        cookie_service.delete_cookie.assert_any_call(response, "access_token")
        cookie_service.delete_cookie.assert_any_call(response, "refresh_token")


class TestRefreshAccessToken:
    """AuthApplicationService.refresh_access_token() 테스트"""

    async def test_refresh_with_valid_token(self, mock_database_context):
        token_service = MagicMock()
        token_service.decode_token.return_value = {"user_account_id": 42}
        token_service.create_token.return_value = "new_access_token"
        cookie_service = MagicMock()

        service = AuthApplicationService(
            token_service=token_service,
            cookie_service=cookie_service,
            kakao_oauth_client=AsyncMock(),
            naver_oauth_client=AsyncMock(),
            google_oauth_client=AsyncMock(),
            github_oauth_client=AsyncMock(),
            domain_event_bus=AsyncMock(),
        )

        response = MagicMock()
        await service.refresh_access_token(response, "valid_refresh_token")

        token_service.decode_token.assert_called_once_with("valid_refresh_token")
        token_service.create_token.assert_called_once()
        cookie_service.set_cookie.assert_called_once()

    async def test_refresh_with_none_token_raises(self, mock_database_context):
        service = AuthApplicationService(
            token_service=MagicMock(),
            cookie_service=MagicMock(),
            kakao_oauth_client=AsyncMock(),
            naver_oauth_client=AsyncMock(),
            google_oauth_client=AsyncMock(),
            github_oauth_client=AsyncMock(),
            domain_event_bus=AsyncMock(),
        )

        response = MagicMock()

        with pytest.raises(APIException) as exc_info:
            await service.refresh_access_token(response, None)

        assert exc_info.value.error_code == "INVALID_TOKEN"
