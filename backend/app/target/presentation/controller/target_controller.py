from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.target.presentation.schema.request.target_request import SetTargetRequest
from app.target.presentation.schema.response.target_response import (
    UserTargetsResponse,
    AllTargetsResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

# User target endpoints
user_router = APIRouter(prefix="/user-accounts/me", tags=["user-targets"])


@user_router.post("/target", response_model=ApiResponseSchema[dict])
@inject
async def set_target(
    request: SetTargetRequest,
    current_user: CurrentUser = Depends(get_current_member),
    # target_service = Depends(Provide[Container.target_service])
):
    """
    목표 설정

    Args:
        request: 목표 코드 (CT, DAILY, BEGINNER)

    Returns:
        빈 데이터
    """
    # TODO: Implement set target logic
    # 1. Validate target code
    # 2. Set target for user

    return ApiResponse(data={})


# Baekjoon target endpoints
baekjoon_router = APIRouter(prefix="/bj-accounts/me", tags=["bj-targets"])


@baekjoon_router.get("/targets", response_model=ApiResponseSchema[UserTargetsResponse])
@inject
async def get_user_targets(
    current_user: CurrentUser = Depends(get_current_member),
    # target_service = Depends(Provide[Container.target_service])
):
    """
    유저 목표 조회

    Returns:
        유저의 목표 목록
    """
    # TODO: Implement get user targets logic
    # 1. Get targets for current user

    response_data = UserTargetsResponse(targets=[])

    return ApiResponse(data=response_data.model_dump(by_alias=True))


# Public target endpoints
router = APIRouter(prefix="/targets", tags=["targets"])


@router.get("", response_model=ApiResponseSchema[AllTargetsResponse])
@inject
async def get_all_targets(
    # target_service = Depends(Provide[Container.target_service])
):
    """
    모든 목표 조회 (인증 불필요)

    Returns:
        모든 목표 목록
    """
    # TODO: Implement get all targets logic
    # 1. Get all available targets

    response_data = AllTargetsResponse(targets=[])

    return ApiResponse(data=response_data.model_dump(by_alias=True))
