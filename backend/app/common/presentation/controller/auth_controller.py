from fastapi import APIRouter, Depends, Request, Response
from dependency_injector.wiring import inject, Provide
from fastapi.responses import RedirectResponse

from app.common.application.command.social_login_command import SocialLoginCommand
from app.common.application.service.auth_application_service import AuthApplicationService
from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/login/{provider}", response_model=ApiResponseSchema[dict])
@inject
async def social_login(
    provider: str,
    frontend_redirect_url: str | None = None,
    auth_application_service: AuthApplicationService = Depends(Provide[Container.auth_application_service])
):
    """
    소셜 로그인 요청 (네이버, 카카오, 구글, 깃허브)

    Args:
        provider: kakao, google, naver, github

    Returns:
        쿠키에 access_token, refresh_token 설정
    """
    
    login_url = await auth_application_service.get_social_login_url(SocialLoginCommand(provider=provider, 
                                                                                 frontend_redirect_url=frontend_redirect_url))
    
    return RedirectResponse(url=login_url, status_code=302)


@router.post("/logout", response_model=ApiResponseSchema[dict])
@inject
async def logout(
    response: Response,
    current_user: CurrentUser = Depends(get_current_member)
):
    """
    로그아웃

    Returns:
        쿠키 삭제
    """
    # TODO: Implement logout logic
    # 1. Clear cookies
    # 2. Invalidate refresh token (if stored in DB/Redis)

    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return ApiResponse(data={})


@router.post("/token/refresh", response_model=ApiResponseSchema[dict])
@inject
async def refresh_token(
    # refresh_token: str = Cookie(None),
    # auth_application_service: AuthApplicationService = Depends(Provide[Container.auth_application_service])
):
    """
    리프레시 토큰 재발급

    Returns:
        새로운 access_token, refresh_token
    """
    # TODO: Implement token refresh logic
    # 1. Validate refresh token
    # 2. Generate new tokens
    # 3. Set cookies

    return ApiResponse(data={})
