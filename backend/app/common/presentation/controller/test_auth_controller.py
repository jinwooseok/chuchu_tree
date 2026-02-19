"""
성능/부하 테스트 전용 인증 API
- local, dev 환경에서만 라우터가 등록됨
- prod 환경에서는 엔드포인트 자체가 존재하지 않음
"""
import os
import uuid
from datetime import timedelta

from fastapi import APIRouter, Depends, Response
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel, Field

from app.common.application.service.auth_application_service import AuthApplicationService
from app.common.domain.entity.auth_event_payloads import (
    SocialLoginSuccessedPayload,
    FindUserAccountResultPayload,
)
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import Provider
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

router = APIRouter(prefix="/test/auth", tags=["test-auth"])


# ── Request/Response DTOs ──

class TestRegisterRequest(BaseModel):
    username: str = Field(
        default_factory=lambda: f"test_{uuid.uuid4().hex[:8]}",
        description="테스트 유저 식별자 (provider_id로 사용됨)",
    )
    email: str | None = Field(default=None, description="이메일 (선택)")


class TestLoginRequest(BaseModel):
    username: str = Field(..., description="등록 시 사용한 username (provider_id)")


class TestRegisterResponse(BaseModel):
    user_account_id: int
    username: str


class TestLoginResponse(BaseModel):
    user_account_id: int
    username: str


class TestTokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    user_account_id: int


# ── 환경 검증 ──

def _assert_non_production():
    env = os.getenv("environment", "local")
    if env == "prod":
        raise APIException(ErrorCode.INVALID_REQUEST)


async def _find_or_create_user(
    auth_application_service: AuthApplicationService,
    username: str,
    email: str | None = None,
) -> FindUserAccountResultPayload:
    event = DomainEvent(
        event_type="SOCIAL_LOGIN_SUCCESSED",
        data=SocialLoginSuccessedPayload(
            provider=Provider.NONE.value,
            provider_id=username,
            email=email,
        ),
        result_type=FindUserAccountResultPayload,
    )
    return await auth_application_service.domain_event_bus.publish(event)


# ── 엔드포인트 ──

@router.post("/register", response_model=ApiResponseSchema[TestRegisterResponse])
@inject
async def test_register(
    body: TestRegisterRequest,
    response: Response,
    auth_application_service: AuthApplicationService = Depends(
        Provide[Container.auth_application_service]
    ),
):
    """
    테스트 유저 생성 및 JWT 토큰 발급 (쿠키 설정)
    - Provider.NONE으로 유저를 생성
    - provider_id = body.username
    """
    _assert_non_production()

    result = await _find_or_create_user(
        auth_application_service, body.username, body.email
    )

    auth_application_service._create_and_set_tokens(
        response, result.user_account_id
    )

    return ApiResponse(
        TestRegisterResponse(
            user_account_id=result.user_account_id,
            username=body.username,
        )
    )


@router.post("/login", response_model=ApiResponseSchema[TestLoginResponse])
@inject
async def test_login(
    body: TestLoginRequest,
    response: Response,
    auth_application_service: AuthApplicationService = Depends(
        Provide[Container.auth_application_service]
    ),
):
    """
    테스트 유저 로그인 (기존 유저 조회 후 JWT 쿠키 설정)
    - Provider.NONE + provider_id 조합으로 유저 조회
    - 존재하지 않으면 자동 생성
    """
    _assert_non_production()

    result = await _find_or_create_user(
        auth_application_service, body.username
    )

    auth_application_service._create_and_set_tokens(
        response, result.user_account_id
    )

    return ApiResponse(
        TestLoginResponse(
            user_account_id=result.user_account_id,
            username=body.username,
        )
    )


@router.post("/token", response_model=ApiResponseSchema[TestTokenResponse])
@inject
async def test_get_token(
    body: TestLoginRequest,
    response: Response,
    auth_application_service: AuthApplicationService = Depends(
        Provide[Container.auth_application_service]
    ),
):
    """
    테스트 유저의 JWT 토큰을 Response Body로 직접 반환
    (쿠키 없이 토큰만 필요한 부하 테스트 도구용)
    """
    _assert_non_production()

    result = await _find_or_create_user(
        auth_application_service, body.username
    )

    access_token = auth_application_service.token_service.create_token(
        payload={"user_account_id": result.user_account_id},
        expires_delta=timedelta(hours=6),
    )
    refresh_token = auth_application_service.token_service.create_token(
        payload={"user_account_id": result.user_account_id},
        expires_delta=timedelta(days=7),
    )

    return ApiResponse(
        TestTokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user_account_id=result.user_account_id,
        )
    )


@router.delete("/cleanup", response_model=ApiResponseSchema[dict])
@inject
async def test_cleanup(
    auth_application_service: AuthApplicationService = Depends(
        Provide[Container.auth_application_service]
    ),
):
    """
    테스트 유저 전체 삭제 (Provider.NONE인 유저)

    Hard Delete로 연관 데이터 모두 삭제:
    - user_account (테스트 유저)
    - account_link (백준 계정 연동)
    - bj_account (백준 계정)
    - problem_history (문제 풀이 기록)
    - streak (스트릭 기록)
    - tag_skill_history (태그 숙련도 이력)
    - user_target (목표)
    - tag_customization (태그 커스터마이징)
    - problem_record (문제 기록)
    - will_solve_problem (풀 예정 문제)
    - problem_banned_record (제외 문제)

    부하 테스트 후 실행 필수!
    """
    _assert_non_production()

    # 이벤트 발행으로 삭제 요청
    event = DomainEvent(
        event_type="TEST_USERS_CLEANUP_REQUESTED",
        data={"provider": Provider.NONE.value},
        result_type=dict,
    )

    result = await auth_application_service.domain_event_bus.publish(event)

    return ApiResponse({
        "deleted_count": result.get("deleted_count", 0),
        "message": f"Deleted {result.get('deleted_count', 0)} test users and all related data"
    })
