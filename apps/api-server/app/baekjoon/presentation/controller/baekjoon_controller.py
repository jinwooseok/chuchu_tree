from datetime import date as date_type
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.baekjoon.application.command.get_unrecorded_problems_command import GetUnrecordedProblemsCommand
from app.baekjoon.application.command.link_bj_account_command import LinkBjAccountCommand
from app.baekjoon.application.command.get_baekjoon_me_command import GetBaekjoonMeCommand
from app.baekjoon.application.command.get_monthly_problems_command import GetMonthlyProblemsCommand
from app.baekjoon.application.command.get_streaks_command import GetStreaksCommand
from app.baekjoon.application.query.baekjoon_account_info_query import BaekjoonMeQuery
from app.baekjoon.application.query.get_unrecorded_problems_query import GetUnrecordedProblemsQuery
from app.baekjoon.application.usecase.get_scheduler_inactive_periods_usecase import GetSchedulerInactivePeriodsUsecase
from app.baekjoon.application.usecase.get_unrecorded_problems_usecase import GetUnrecordedProblemsUsecase
from app.baekjoon.application.usecase.link_bj_account_usecase import LinkBjAccountUsecase
from app.baekjoon.application.usecase.get_baekjoon_me_usecase import GetBaekjoonMeUsecase
from app.baekjoon.application.usecase.get_monthly_problems_usecase import GetMonthlyProblemsUsecase
from app.baekjoon.application.usecase.get_streaks_usecase import GetStreaksUsecase
from app.baekjoon.application.usecase.update_bj_account_usecase import UpdateBjAccountUsecase
from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.baekjoon.presentation.schema.request.baekjoon_request import (
    LinkBaekjoonAccountRequest
)
from app.baekjoon.presentation.schema.response.get_baekjoon_me_response import (
    GetBaekjoonMeResponse
)
from app.baekjoon.presentation.schema.response.get_monthly_problems_response import (
    GetMonthlyProblemsResponse
)
from app.baekjoon.presentation.schema.response.get_streaks_response import (
    GetStreaksResponse
)
from app.baekjoon.presentation.schema.response.get_scheduler_inactive_periods_response import (
    GetSchedulerInactivePeriodsResponse
)
from app.baekjoon.presentation.schema.response.get_unrecorded_problems_response import (
    GetUnrecordedProblemsResponse
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
    link_bj_account_usecase: LinkBjAccountUsecase = Depends(Provide[Container.link_bj_account_usecase])
):
    """
    백준 계정 연동 변경 (최초 1회 가능 + 7일)

    Args:
        request: 백준 계정 ID

    Returns:
        빈 데이터
    """
    await link_bj_account_usecase.execute(LinkBjAccountCommand(
        user_account_id=current_user.user_account_id, 
        bj_account_id=request.bj_account))
    
    return ApiResponse(data={})


@router.get("/me", response_model=ApiResponseSchema[GetBaekjoonMeResponse])
@inject
async def get_baekjoon_me(
    current_user: CurrentUser = Depends(get_current_member),
    get_baekjoon_me_usecase: GetBaekjoonMeUsecase = Depends(Provide[Container.get_baekjoon_me_usecase])
):
    """
    유저(본인) 기본정보 조회 (유저 정보 + 백준 정보)

    Returns:
        유저 정보, 백준 정보
    """
    # 백준 내 정보 조회
    result: BaekjoonMeQuery = await get_baekjoon_me_usecase.execute(
        GetBaekjoonMeCommand(user_account_id=current_user.user_account_id)
    )

    # Response 객체로 변환
    response_data = GetBaekjoonMeResponse.from_query(result)

    return ApiResponse(data=response_data)


@router.get("/me/streak", response_model=ApiResponseSchema[GetStreaksResponse])
@inject
async def get_baekjoon_streak(
    start_date: date_type = Query(..., alias="startDate", description="시작 날짜 (YYYY-MM-DD)"),
    end_date: date_type = Query(..., alias="endDate", description="끝 날짜 (YYYY-MM-DD)"),
    current_user: CurrentUser = Depends(get_current_member),
    get_streaks_usecase: GetStreaksUsecase = Depends(Provide[Container.get_streaks_usecase])
):
    """
    백준 스트릭 조회 (기간)

    Args:
        start_date: 시작 날짜
        end_date: 끝 날짜

    Returns:
        스트릭 데이터
    """

    # 스트릭 조회
    result = await get_streaks_usecase.execute(
        GetStreaksCommand(
            user_account_id=current_user.user_account_id,
            start_date=start_date,
            end_date=end_date
        )
    )

    # Response 객체로 변환
    response_data = GetStreaksResponse.from_query(result)

    return ApiResponse(data=response_data)


@router.get("/me/problems", response_model=ApiResponseSchema[GetMonthlyProblemsResponse])
@inject
async def get_monthly_problems(
    year: int = Query(..., ge=2020, description="월 (1-12)"),
    month: int = Query(..., ge=1, le=12, description="월 (1-12)"),
    current_user: CurrentUser = Depends(get_current_member),
    get_monthly_problems_usecase: GetMonthlyProblemsUsecase = Depends(Provide[Container.get_monthly_problems_usecase])
):
    """
    월간 문제 상세 정보 조회 (SOLVED LIST, WILL SOLVED LIST)

    Args:
        month: 월 (1-12)

    Returns:
        월간 문제 데이터
    """
    # 월간 문제 조회
    result = await get_monthly_problems_usecase.execute(
        GetMonthlyProblemsCommand(
            user_account_id=current_user.user_account_id,
            year=year,
            month=month
        )
    )

    # Response 객체로 변환
    response_data = GetMonthlyProblemsResponse.from_query(result)

    return ApiResponse(data=response_data)

@router.get("/unrecorded-problems/me", response_model=ApiResponseSchema[GetUnrecordedProblemsResponse])
@inject
async def get_unrecorded_problems_me(
    current_user: CurrentUser = Depends(get_current_member),
    get_unrecorded_problems_usecase: GetUnrecordedProblemsUsecase = Depends(Provide[Container.get_unrecorded_problems_usecase])
):
    """
    유저의 실제로 푼 문제 조회 (solved.ac 기준)

    Returns:
        기록되지 않은 문제 목록
    """
    # 기록되지 않은 문제 조회
    query: GetUnrecordedProblemsQuery = await get_unrecorded_problems_usecase.execute(
        GetUnrecordedProblemsCommand(user_account_id=current_user.user_account_id)
    )

    # Response 객체로 변환
    return ApiResponse(data=GetUnrecordedProblemsResponse.from_query(query))

@router.get("/me/scheduler-inactive-periods", response_model=ApiResponseSchema[GetSchedulerInactivePeriodsResponse])
@inject
async def get_scheduler_inactive_periods(
    current_user: CurrentUser = Depends(get_current_member),
    get_scheduler_inactive_periods_usecase: GetSchedulerInactivePeriodsUsecase = Depends(
        Provide[Container.get_scheduler_inactive_periods_usecase]
    )
):
    """
    스케줄러 미작동 구간 조회

    연동일부터 오늘까지 스케줄러 SUCCESS 기록이 없는 날짜 구간을 반환합니다.

    Returns:
        미작동 구간 목록
    """
    result = await get_scheduler_inactive_periods_usecase.execute(
        user_account_id=current_user.user_account_id
    )
    return ApiResponse(data=GetSchedulerInactivePeriodsResponse.from_query(result))


@router.post("/me/refresh", response_model=ApiResponseSchema[dict])
@inject
async def refresh_problem_data(
    current_user: CurrentUser = Depends(get_current_member),
    update_bj_account_usecase:UpdateBjAccountUsecase = Depends(Provide[Container.update_bj_account_usecase])
):
    """
    새로고침 (solved.ac에서 최신 데이터 가져오기)

    Returns:
        빈 데이터
    """
    await update_bj_account_usecase.execute(current_user.user_account_id)

    return ApiResponse(data={})


# # Admin endpoints
# admin_router = APIRouter(prefix="/admin/bj-accounts", tags=["admin-bj-accounts"])


# @admin_router.get("", response_model=ApiResponseSchema[AdminBaekjoonAccountsResponse])
# @inject
# async def get_all_baekjoon_accounts(
#     page: int = Query(1, ge=1, description="페이지 번호"),
#     current_user: CurrentUser = Depends(get_current_member),
#     # baekjoon_service = Depends(Provide[Container.baekjoon_service])
# ):
#     """
#     모든 백준 계정 조회 (ADMIN)

#     Args:
#         page: 페이지 번호

#     Returns:
#         백준 계정 목록
#     """
#     # TODO: Implement admin baekjoon accounts list logic
#     # 1. Check admin permission
#     # 2. Get paginated baekjoon accounts

#     response_data = AdminBaekjoonAccountsResponse(bjAccounts=[])

#     return ApiResponse(data=response_data.model_dump(by_alias=True))
