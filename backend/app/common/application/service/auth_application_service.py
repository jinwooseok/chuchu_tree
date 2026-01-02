import logging
from typing import Optional

from app.common.application.command.social_login_command import SocialLoginCommand
from app.common.domain.enums import Provider
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
            kakao_oauth_client: OAuthClient,
            naver_oauth_client: OAuthClient
    ):
        self.token_service = token_service
        self.kakao_oauth_client = kakao_oauth_client
        self.naver_oauth_client = naver_oauth_client
    
    def authenticate_member(self, token: Optional[str]) -> CurrentUser:
        """사용자 인증 - Application Layer 로직"""
        if not token:
            raise APIException(ErrorCode.NO_LOGIN_STATUS)
        
        payload = self.token_service.decode_token(token)
        member_id = payload.get("member_id")
        position = payload.get("position")
        if member_id is None:
            raise APIException(ErrorCode.AUTHORIZATION_FAILED)
        if position is None:
            raise APIException(ErrorCode.AUTHORIZATION_FAILED)
        
        return CurrentUser(member_id, position)
    
    @transactional
    async def get_social_login_url(self, command: SocialLoginCommand) -> str:
        """소셜 로그인 URL 생성"""
        
        if command.provider == Provider.NAVER:
            return self.naver_oauth_client.get_social_login_url(command.frontend_redirect_url)

        elif command.provider == Provider.KAKAO:
            return self.kakao_oauth_client.get_social_login_url(command.frontend_redirect_url)
        
        else:
            raise APIException(ErrorCode.INVALID_PROVIDER)