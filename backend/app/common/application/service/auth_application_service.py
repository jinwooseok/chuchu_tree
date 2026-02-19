from datetime import timedelta
import logging
import base64
import json
from typing import Optional

from fastapi import Response

from app.common.application.command.social_login_command import SocialLoginCommand
from app.common.application.command.social_login_callback_command import SocialLoginCallbackCommand
from app.common.domain.entity.auth_event_payloads import FindUserAccountResultPayload, SocialLoginSuccessedPayload, UserAccountWithdrawalPayload
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
from app.user.application.command.get_user_account_info_command import GetUserAccountInfoCommand
from app.user.application.query.user_account_info_query import GetUserAccountInfoQuery

from app.common.domain.gateway.refresh_token_whitelist_gateway import RefreshTokenWhitelistGateway

logger = logging.getLogger()

RT_TTL_SECONDS = 7 * 24 * 60 * 60  # 7일


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
            domain_event_bus: DomainEventBus,
            refresh_token_whitelist: RefreshTokenWhitelistGateway
    ):
        self.token_service = token_service
        self.cookie_service = cookie_service
        self.kakao_oauth_client = kakao_oauth_client
        self.naver_oauth_client = naver_oauth_client
        self.google_oauth_client = google_oauth_client
        self.github_oauth_client = github_oauth_client
        self.domain_event_bus = domain_event_bus
        self.refresh_token_whitelist = refresh_token_whitelist
    
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
            action = state_data.get("action")
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
                provider_id=user_info.provider_id,
                email=user_info.email
            ),
            result_type=FindUserAccountResultPayload
        )
    
        user_account:FindUserAccountResultPayload = await self.domain_event_bus.publish(event)
        
        if action == "withdraw":
            try:
                await oauth_client.unlink(oauth_token.access_token)
                logger.info(f"OAuth 연동 해제 성공: provider={provider_enum}, user_id={user_account.user_account_id}")
            except Exception as e:
                logger.warning(f"OAuth 연동 해제 실패 (계속 진행): {e}")

            if not user_account:
                logger.error(f"사용자를 찾을 수 없음: provider={provider_enum}, provider_id={user_info.provider_id}")
                raise APIException(ErrorCode.INVALID_REQUEST)

            # 회원 탈퇴 이벤트 발행 (User, Activity 도메인에서 각자 데이터 삭제)
            withdrawal_event = DomainEvent(
                event_type="USER_ACCOUNT_WITHDRAWAL_REQUESTED",
                data=UserAccountWithdrawalPayload(user_account_id=user_account.user_account_id),
                result_type=None  # Fire-and-Forget
            )
            await self.domain_event_bus.publish(withdrawal_event)
            logger.info(f"회원 탈퇴 처리 완료: user_id={user_account.user_account_id}")

            # RT 전체 폐기 + 쿠키 삭제
            await self.refresh_token_whitelist.revoke_all_user_tokens(user_account.user_account_id)
            self._clear_auth_cookies(command.response)
        else:
            # JWT 토큰 생성 및 쿠키 설정
            await self._create_and_set_tokens(command.response, user_account.user_account_id)
        
        return frontend_redirect_url
    
    async def logout(self, response: Response, user_account_id: int):
        await self.refresh_token_whitelist.revoke_all_user_tokens(user_account_id)
        self._clear_auth_cookies(response)
    
    @transactional(readonly=True)
    async def get_withdraw_url(self, user_account_id: int, frontend_redirect_url: str | None) -> str:
        """
        회원탈퇴용 OAuth 인증 URL 생성

        Args:
            user_account_id: 사용자 계정 ID
            frontend_redirect_url: 프론트엔드 리다이렉트 URL

        Returns:
            OAuth 인증 URL
        """
        # 사용자 계정 정보 조회 이벤트 발행
        event = DomainEvent(
            event_type="GET_USER_ACCOUNT_INFO_REQUESTED",
            data=GetUserAccountInfoCommand(user_account_id=user_account_id),
            result_type=GetUserAccountInfoQuery
        )

        user_account_info: GetUserAccountInfoQuery = await self.domain_event_bus.publish(event)

        # provider 문자열을 enum으로 변환
        provider_enum = Provider(user_account_info.provider)
        oauth_client = self._get_oauth_client(provider_enum)
        return await oauth_client.get_social_login_url(frontend_redirect_url, action="withdraw")

    async def refresh_access_token(self, response: Response, refresh_token: Optional[str]):
        if refresh_token is None:
            raise APIException(ErrorCode.INVALID_TOKEN)

        payload = self.token_service.decode_token(refresh_token)
        user_account_id = payload.get("user_account_id")
        jti = payload.get("jti")

        if not user_account_id or not jti:
            raise APIException(ErrorCode.INVALID_TOKEN)

        # 1. 재사용 감지: 이미 사용된 RT인지 확인
        used_by = await self.refresh_token_whitelist.is_token_used(jti)
        if used_by is not None:
            # 토큰 재사용 감지 → 해당 유저의 모든 RT 삭제
            await self.refresh_token_whitelist.revoke_all_user_tokens(user_account_id)
            raise APIException(ErrorCode.TOKEN_REUSE_DETECTED)

        # 2. 화이트리스트 확인
        is_valid = await self.refresh_token_whitelist.is_token_valid(user_account_id, jti)
        if not is_valid:
            raise APIException(ErrorCode.INVALID_TOKEN)

        # 3. 기존 RT 폐기 + 사용 기록
        await self.refresh_token_whitelist.revoke_token(user_account_id, jti)
        await self.refresh_token_whitelist.mark_as_used(jti, user_account_id, RT_TTL_SECONDS)

        # 4. 새 AT + RT 발급
        new_access_token = self.token_service.create_token(
            payload={"user_account_id": user_account_id},
            expires_delta=timedelta(hours=6)
        )
        new_refresh_token, new_jti = self.token_service.create_refresh_token(
            payload={"user_account_id": user_account_id},
            expires_delta=timedelta(days=7)
        )

        # 5. 새 RT를 화이트리스트에 저장
        await self.refresh_token_whitelist.store_token(user_account_id, new_jti, RT_TTL_SECONDS)

        # 6. 쿠키에 새 AT + RT 설정
        self._set_auth_cookies(response, new_access_token, new_refresh_token)

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
        
    async def _create_and_set_tokens(self, response: Response, user_account_id: int):
        """JWT 토큰 생성 및 쿠키 설정"""
        access_token = self.token_service.create_token(
            payload={
                "user_account_id": user_account_id
            },
            expires_delta=timedelta(minutes=60)
        )

        refresh_token, jti = self.token_service.create_refresh_token(
            payload={
                "user_account_id": user_account_id
            },
            expires_delta=timedelta(days=7)
        )

        # RT를 Redis 화이트리스트에 저장
        await self.refresh_token_whitelist.store_token(user_account_id, jti, RT_TTL_SECONDS)

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