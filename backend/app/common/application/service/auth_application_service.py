from datetime import timedelta
import logging
import base64
import json
from typing import Optional

from fastapi import Response

from app.common.application.command.social_login_command import SocialLoginCommand
from app.common.application.command.social_login_callback_command import SocialLoginCallbackCommand
from app.common.domain.entity.auth_event_payloads import FindUserAccountResultPayload, SocialLoginSuccessedPayload
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import Provider
from app.common.domain.service.cookie_service import CookieService
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.service.oauth_client import OAuthClient
from app.common.domain.vo.current_user import CurrentUser
from app.common.domain.service.token_service import TokenService
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger()
class AuthApplicationService:
    """인증 관련 Application Service"""
    def __init__(
            self,
            token_service: TokenService,
            cookie_service: CookieService,
            kakao_oauth_client: OAuthClient,
            naver_oauth_client: OAuthClient,
            google_oauth_client: OAuthClient,
            github_oauth_client: OAuthClient,
            domain_event_bus: DomainEventBus
    ):
        self.token_service = token_service
        self.cookie_service = cookie_service
        self.kakao_oauth_client = kakao_oauth_client
        self.naver_oauth_client = naver_oauth_client
        self.google_oauth_client = google_oauth_client
        self.github_oauth_client = github_oauth_client
        self.domain_event_bus = domain_event_bus
    
    def authenticate_user(self, token: Optional[str]) -> CurrentUser:
        """사용자 인증 - Application Layer 로직"""
        if not token:
            raise APIException(ErrorCode.NO_LOGIN_STATUS)
        
        payload = self.token_service.decode_token(token)
        user_account_id = payload.get("user_account_id")
        if user_account_id is None:
            raise APIException(ErrorCode.AUTHORIZATION_FAILED)
        
        return CurrentUser(user_account_id)
    
    async def get_social_login_url(self, command: SocialLoginCommand) -> str:
        """소셜 로그인 URL 생성"""
        provider = Provider(command.provider)
        return await self._get_oauth_client(provider).get_social_login_url(command.frontend_redirect_url)

    @transactional
    async def handle_social_login_callback(
        self,
        command: SocialLoginCallbackCommand
    ) -> str:
        """
        OAuth 콜백 처리 및 CSRF 토큰 검증

        Args:
            command: 소셜 로그인 콜백 Command (provider, code, state, request, response 포함)

        Returns:
            프론트엔드 리다이렉트 URL
        """
        # State 디코딩
        try:
            state_data = json.loads(base64.b64decode(command.state.encode()).decode())
            csrf_token = state_data.get("csrf_token")
            frontend_redirect_url = state_data.get("frontend_redirect_url")
        except Exception as e:
            logger.error(f"State 디코딩 실패: {e}")
            raise APIException(ErrorCode.INVALID_REQUEST)

        # CSRF 토큰 검증
        provider_enum = Provider(command.provider)
        oauth_client = self._get_oauth_client(provider_enum)

        is_valid = await oauth_client.verify_csrf_token(csrf_token)
        if not is_valid:
            logger.error(f"CSRF 토큰 검증 실패: {csrf_token}")
            raise APIException(ErrorCode.INVALID_CSRF_TOKEN)

        # OAuth 액세스 토큰 획득
        oauth_token = await oauth_client.get_access_token(command.code, command.state)

        # 사용자 정보 조회
        user_info = await oauth_client.get_user_info(oauth_token.access_token)

        # - 사용자 조회 또는 신규 가입 (user_info.provider_id, user_info.nickname 사용)
        # 이벤트 발행
        event = DomainEvent(
            event_type="SOCIAL_LOGIN_SUCCESSED",
            data=SocialLoginSuccessedPayload(
                provider=user_info.provider.value,
                provider_id=user_info.provider_id
            ),
            result_type=FindUserAccountResultPayload
        )

        user_account:FindUserAccountResultPayload = await self.domain_event_bus.publish(event)

        # JWT 토큰 생성 및 쿠키 설정
        self._create_and_set_tokens(command.response, user_account.user_account_id)

        return frontend_redirect_url
    
    @transactional
    async def logout(self, response: Response):
        self._clear_auth_cookies(response)
        
    @transactional
    async def refresh_access_token(self, response: Response, refresh_token: Optional[str]):
        if refresh_token is None:
            raise APIException(ErrorCode.INVALID_TOKEN)
        
        payload = self.token_service.decode_token(refresh_token)
        
        new_access_token = self.token_service.create_token(
            payload={
                "user_account_id": payload["user_account_id"],
            },
            expires_delta=timedelta(hours=6)
        )
        
        self._set_access_token_cookie(response, new_access_token)

    def _get_oauth_client(self, provider: Provider) -> OAuthClient:
        """Provider에 맞는 OAuth 클라이언트 반환"""
        if provider == Provider.NAVER:
            return self.naver_oauth_client
        elif provider == Provider.KAKAO:
            return self.kakao_oauth_client
        elif provider == Provider.GOOGLE:
            return self.google_oauth_client
        elif provider == Provider.GITHUB:
            return self.github_oauth_client
        else:
            raise APIException(ErrorCode.INVALID_PROVIDER)
        
    def _create_and_set_tokens(self, response: Response, user_account_id: int):
        """JWT 토큰 생성 및 쿠키 설정"""
        access_token = self.token_service.create_token(
            payload={
                "user_account_id": user_account_id
            },
            expires_delta=timedelta(hours=6)
        )

        refresh_token = self.token_service.create_token(
            payload={
                "user_account_id": user_account_id
            },
            expires_delta=timedelta(days=7)
        )

        self._set_auth_cookies(response, access_token, refresh_token)

    def _set_auth_cookies(self, response: Response, access_token: str, refresh_token: str):
        self.cookie_service.set_cookie(response,
                                       "access_token",
                                       access_token,
                                       max_age=6 * 60 * 60)

        self.cookie_service.set_cookie(response,
                                       "refresh_token",
                                       refresh_token,
                                       max_age=7 * 24 * 60 * 60)
    
    def _set_access_token_cookie(self, response: Response, access_token: str):
        self.cookie_service.set_cookie(response, 
                                     "access_token", 
                                     access_token, 
                                     max_age=6 * 60 * 60)
    
    def _clear_auth_cookies(self, response: Response):
        # 설정할 때와 동일한 속성으로 삭제
        self.cookie_service.delete_cookie(response, "access_token")
        self.cookie_service.delete_cookie(response, "refresh_token")