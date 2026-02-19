import pytest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from app.common.application.command.social_login_command import SocialLoginCommand
from app.common.application.service.auth_application_service import AuthApplicationService
from app.common.domain.enums import Provider
from app.common.domain.vo.current_user import CurrentUser
from app.core.exception import APIException


def _make_service(decode_return=None, whitelist=None) -> AuthApplicationService:
    """공통 서비스 팩토리"""
    token_service = MagicMock()
    if decode_return is not None:
        token_service.decode_token.return_value = decode_return
    cookie_service = MagicMock()
    domain_event_bus = AsyncMock()
    rt_whitelist = whitelist or AsyncMock()

    return AuthApplicationService(
        token_service=token_service,
        cookie_service=cookie_service,
        kakao_oauth_client=AsyncMock(),
        naver_oauth_client=AsyncMock(),
        google_oauth_client=AsyncMock(),
        github_oauth_client=AsyncMock(),
        domain_event_bus=domain_event_bus,
        refresh_token_whitelist=rt_whitelist,
    )


class TestAuthenticateUser:
    """AuthApplicationService.authenticate_user() 테스트"""

    def test_valid_token_returns_current_user(self):
        service = _make_service(decode_return={"user_account_id": 42})

        result = service.authenticate_user("valid_token")

        assert isinstance(result, CurrentUser)
        assert result.user_account_id == 42

    def test_none_token_raises_no_login_status(self):
        service = _make_service()

        with pytest.raises(APIException) as exc_info:
            service.authenticate_user(None)

        assert exc_info.value.error_code == "NO_LOGIN_STATUS"

    def test_empty_token_raises_no_login_status(self):
        service = _make_service()

        with pytest.raises(APIException) as exc_info:
            service.authenticate_user("")

        assert exc_info.value.error_code == "NO_LOGIN_STATUS"

    def test_token_without_user_id_raises_authorization_failed(self):
        service = _make_service(decode_return={})

        with pytest.raises(APIException) as exc_info:
            service.authenticate_user("some_token")

        assert exc_info.value.error_code == "AUTHORIZATION_FAILED"

    def test_expired_token_propagates_exception(self):
        service = _make_service()
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
            refresh_token_whitelist=AsyncMock(),
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

    async def test_logout_clears_cookies_and_revokes_tokens(self, mock_database_context):
        cookie_service = MagicMock()
        rt_whitelist = AsyncMock()
        service = AuthApplicationService(
            token_service=MagicMock(),
            cookie_service=cookie_service,
            kakao_oauth_client=AsyncMock(),
            naver_oauth_client=AsyncMock(),
            google_oauth_client=AsyncMock(),
            github_oauth_client=AsyncMock(),
            domain_event_bus=AsyncMock(),
            refresh_token_whitelist=rt_whitelist,
        )

        response = MagicMock()
        await service.logout(response, user_account_id=42)

        # RT 전체 폐기 확인
        rt_whitelist.revoke_all_user_tokens.assert_called_once_with(42)

        # 쿠키 삭제 확인
        assert cookie_service.delete_cookie.call_count == 2
        cookie_service.delete_cookie.assert_any_call(response, "access_token")
        cookie_service.delete_cookie.assert_any_call(response, "refresh_token")


class TestRefreshAccessToken:
    """AuthApplicationService.refresh_access_token() RTR 테스트"""

    async def test_refresh_with_none_token_raises(self, mock_database_context):
        service = _make_service()

        response = MagicMock()

        with pytest.raises(APIException) as exc_info:
            await service.refresh_access_token(response, None)

        assert exc_info.value.error_code == "INVALID_TOKEN"

    async def test_refresh_without_jti_raises(self, mock_database_context):
        """jti가 없는 토큰은 INVALID_TOKEN"""
        service = _make_service(decode_return={"user_account_id": 42})

        response = MagicMock()

        with pytest.raises(APIException) as exc_info:
            await service.refresh_access_token(response, "old_format_token")

        assert exc_info.value.error_code == "INVALID_TOKEN"

    async def test_refresh_token_reuse_detected(self, mock_database_context):
        """이미 사용된 RT로 요청하면 TOKEN_REUSE_DETECTED + 전체 RT 삭제"""
        rt_whitelist = AsyncMock()
        rt_whitelist.is_token_used.return_value = 42  # 이미 사용됨
        service = _make_service(
            decode_return={"user_account_id": 42, "jti": "used-jti"},
            whitelist=rt_whitelist
        )

        response = MagicMock()

        with pytest.raises(APIException) as exc_info:
            await service.refresh_access_token(response, "reused_token")

        assert exc_info.value.error_code == "TOKEN_REUSE_DETECTED"
        rt_whitelist.revoke_all_user_tokens.assert_called_once_with(42)

    async def test_refresh_token_not_in_whitelist_raises(self, mock_database_context):
        """화이트리스트에 없는 RT는 INVALID_TOKEN"""
        rt_whitelist = AsyncMock()
        rt_whitelist.is_token_used.return_value = None  # 사용 기록 없음
        rt_whitelist.is_token_valid.return_value = False  # 화이트리스트에 없음
        service = _make_service(
            decode_return={"user_account_id": 42, "jti": "unknown-jti"},
            whitelist=rt_whitelist
        )

        response = MagicMock()

        with pytest.raises(APIException) as exc_info:
            await service.refresh_access_token(response, "unknown_token")

        assert exc_info.value.error_code == "INVALID_TOKEN"

    async def test_refresh_success_rtr_flow(self, mock_database_context):
        """정상 RTR 흐름: 기존 RT 폐기 → 새 AT+RT 발급 → 화이트리스트 저장"""
        rt_whitelist = AsyncMock()
        rt_whitelist.is_token_used.return_value = None  # 사용 안 됨
        rt_whitelist.is_token_valid.return_value = True  # 화이트리스트에 있음

        service = _make_service(
            decode_return={"user_account_id": 42, "jti": "valid-jti"},
            whitelist=rt_whitelist
        )
        service.token_service.create_token.return_value = "new_access_token"
        service.token_service.create_refresh_token.return_value = ("new_refresh_token", "new-jti")

        response = MagicMock()
        await service.refresh_access_token(response, "valid_refresh_token")

        # 1. 기존 RT 폐기
        rt_whitelist.revoke_token.assert_called_once_with(42, "valid-jti")

        # 2. 기존 RT를 사용됨으로 기록
        rt_whitelist.mark_as_used.assert_called_once_with("valid-jti", 42, 7 * 24 * 60 * 60)

        # 3. 새 RT를 화이트리스트에 저장
        rt_whitelist.store_token.assert_called_once_with(42, "new-jti", 7 * 24 * 60 * 60)

        # 4. 쿠키에 AT + RT 설정
        cookie_calls = service.cookie_service.set_cookie.call_args_list
        assert len(cookie_calls) == 2
        # access_token 쿠키
        assert cookie_calls[0][0][1] == "access_token"
        assert cookie_calls[0][0][2] == "new_access_token"
        # refresh_token 쿠키
        assert cookie_calls[1][0][1] == "refresh_token"
        assert cookie_calls[1][0][2] == "new_refresh_token"


class TestCreateAndSetTokens:
    """AuthApplicationService._create_and_set_tokens() 테스트"""

    async def test_creates_rt_with_jti_and_stores_in_whitelist(self, mock_database_context):
        rt_whitelist = AsyncMock()
        service = _make_service(whitelist=rt_whitelist)
        service.token_service.create_token.return_value = "access_token_value"
        service.token_service.create_refresh_token.return_value = ("refresh_token_value", "generated-jti")

        response = MagicMock()
        await service._create_and_set_tokens(response, user_account_id=42)

        # create_refresh_token 호출 확인
        service.token_service.create_refresh_token.assert_called_once()

        # Redis 저장 확인
        rt_whitelist.store_token.assert_called_once_with(42, "generated-jti", 7 * 24 * 60 * 60)

        # 쿠키 설정 확인
        cookie_calls = service.cookie_service.set_cookie.call_args_list
        assert len(cookie_calls) == 2
