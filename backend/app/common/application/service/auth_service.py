import logging
from typing import Optional

from app.common.domain.vo.current_user import CurrentUser
from app.common.domain.service.token_service import TokenService
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger()
class AuthService:
    """인증 관련 Application Service"""
    def __init__(
            self,
            token_service: TokenService,
    ):
        self.token_service = token_service
    
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