from fastapi import APIRouter, Depends, Response
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/login/{provider}", response_model=ApiResponseSchema[dict])
@inject
async def social_login(
    provider: str,
    # auth_service: AuthService = Depends(Provide[Container.auth_service])
):
    """
    소셜 로그인 요청 (네이버, 카카오, 구글, 깃허브)

    Args:
        provider: kakao, google, naver, github

    Returns:
        쿠키에 access_token, refresh_token 설정
    """
    # TODO: Implement OAuth login logic
    # 1. Redirect to OAuth provider
    # 2. Handle callback
    # 3. Create/Update user account
    # 4. Generate tokens
    # 5. Set cookies

    return ApiResponse(data={})


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
    # auth_service: AuthService = Depends(Provide[Container.auth_service])
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
