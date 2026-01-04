from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
from app.baekjoon.application.usecase.link_bj_account_usecase import LinkBjAccountUsecase
from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.baekjoon.presentation.schema.request.baekjoon_request import (
    LinkBaekjoonAccountRequest
)
from app.baekjoon.presentation.schema.response.baekjoon_response import (
    BaekjoonMeResponse,
    StreakResponse,
    MonthlyProblemsResponse,
    AdminBaekjoonAccountsResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/bj-accounts", tags=["bj-accounts"])


@router.post("/link", response_model=ApiResponseSchema[dict])
@inject
async def link_baekjoon_account(
    request: LinkBaekjoonAccountRequest,
    current_user: CurrentUser = Depends(get_current_member),
    link_bj_account_usecase: LinkBjAccountUsecase = Depends(Provide[Container.link_bj_account_usecase])
):
    """
    백준 계정 연동

    Args:
        request: 백준 계정 ID

    Returns:
        빈 데이터
    """
    
    await link_bj_account_usecase.execute(LinkBjAccountCommand(
        user_account_id=current_user.user_account_id, 
        bj_account_id=request.bj_account))
    
    return ApiResponse(data={})


@router.patch("/link", response_model=ApiResponseSchema[dict])
@inject
async def update_baekjoon_account_link(
    request: LinkBaekjoonAccountRequest,
    current_user: CurrentUser = Depends(get_current_member),
    # baekjoon_service = Depends(Provide[Container.baekjoon_service])
):
    """
    백준 계정 연동 변경 (최초 1회 가능 + 7일)

    Args:
        request: 백준 계정 ID

    Returns:
        빈 데이터
    """
    # TODO: Implement baekjoon account update logic
    # 1. Check if update is allowed (first time or 7 days passed)
    # 2. Update linked account
    # 3. Fetch data from solved.ac API

    return ApiResponse(data={})


@router.get("/me", response_model=ApiResponseSchema[BaekjoonMeResponse])
@inject
async def get_baekjoon_me(
    current_user: CurrentUser = Depends(get_current_member),
    # baekjoon_service = Depends(Provide[Container.baekjoon_service])
):
    """
    유저(본인) 기본정보 조회 (정보 + 스트릭)

    Returns:
        유저 정보, 백준 정보, 스트릭
    """
    # TODO: Implement get baekjoon me logic
    # 1. Get user account info
    # 2. Get baekjoon account info
    # 3. Get streak data

    response_data = BaekjoonMeResponse(
        userAccount={
            "userAccountId": 1,
            "profileImageUrl": None,
            "registeredAt": "2025-02-07 00:00:00 TZ"
        },
        bjAccount={
            "bjAccountId": 1,
            "stat": {
                "tierId": 1,
                "tierName": "B5",
                "longestStreak": 55,
                "rating": 1800,
                "class": 7,
                "tierStartDate": "2055-02-07"
            },
            "streaks": [],
            "registeredAt": "2025-02-07 00:00:00 TZ"
        },
        linkedAt="2025-02-07 00:00:00 TZ"
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))


@router.get("/me/streak", response_model=ApiResponseSchema[StreakResponse])
@inject
async def get_baekjoon_streak(
    start_date: str = Query(..., alias="startDate", description="시작 날짜 (YYYY-MM-DD)"),
    end_date: str = Query(..., alias="endDate", description="끝 날짜 (YYYY-MM-DD)"),
    current_user: CurrentUser = Depends(get_current_member),
    # baekjoon_service = Depends(Provide[Container.baekjoon_service])
):
    """
    백준 스트릭 조회 (기간)

    Args:
        start_date: 시작 날짜
        end_date: 끝 날짜

    Returns:
        스트릭 데이터
    """
    # TODO: Implement get streak logic
    # 1. Validate date range
    # 2. Get streak data for the period

    response_data = StreakResponse(streaks=[])

    return ApiResponse(data=response_data.model_dump(by_alias=True))


@router.get("/me/problems", response_model=ApiResponseSchema[MonthlyProblemsResponse])
@inject
async def get_monthly_problems(
    month: int = Query(..., ge=1, le=12, description="월 (1-12)"),
    current_user: CurrentUser = Depends(get_current_member),
    # baekjoon_service = Depends(Provide[Container.baekjoon_service])
):
    """
    월간 문제 상세 정보 조회 (SOLVED LIST, WILL SOLVED LIST)

    Args:
        month: 월 (1-12)

    Returns:
        월간 문제 데이터
    """
    # TODO: Implement get monthly problems logic
    # 1. Get solved problems for the month
    # 2. Get will solve problems for the month

    response_data = MonthlyProblemsResponse(
        totalProblemCount=0,
        monthlyData=[]
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))


@router.post("/me/problem-update", response_model=ApiResponseSchema[dict])
@inject
async def refresh_problem_data(
    current_user: CurrentUser = Depends(get_current_member),
    # baekjoon_service = Depends(Provide[Container.baekjoon_service])
):
    """
    새로고침 (solved.ac에서 최신 데이터 가져오기)

    Returns:
        빈 데이터
    """
    # TODO: Implement problem data refresh logic
    # 1. Fetch latest data from solved.ac API
    # 2. Update database

    return ApiResponse(data={})


# Admin endpoints
admin_router = APIRouter(prefix="/admin/bj-accounts", tags=["admin-bj-accounts"])


@admin_router.get("", response_model=ApiResponseSchema[AdminBaekjoonAccountsResponse])
@inject
async def get_all_baekjoon_accounts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    current_user: CurrentUser = Depends(get_current_member),
    # baekjoon_service = Depends(Provide[Container.baekjoon_service])
):
    """
    모든 백준 계정 조회 (ADMIN)

    Args:
        page: 페이지 번호

    Returns:
        백준 계정 목록
    """
    # TODO: Implement admin baekjoon accounts list logic
    # 1. Check admin permission
    # 2. Get paginated baekjoon accounts

    response_data = AdminBaekjoonAccountsResponse(bjAccounts=[])

    return ApiResponse(data=response_data.model_dump(by_alias=True))
