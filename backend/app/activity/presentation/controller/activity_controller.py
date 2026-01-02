from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.activity.presentation.schema.request.activity_request import (
    UpdateWillSolveProblemsRequest,
    UpdateSolvedProblemsRequest,
    ProblemRecordRequest,
    BanProblemRequest,
    BanTagRequest
)
from app.activity.presentation.schema.response.activity_response import (
    ProblemRecordResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/user-accounts/me", tags=["activity"])


@router.post("/problems/will-solve-problems", response_model=ApiResponseSchema[dict])
@inject
async def update_will_solve_problems(
    request: UpdateWillSolveProblemsRequest,
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    풀 문제 업데이트 (날짜 단위)

    Args:
        request: 날짜, 문제 ID 목록

    Returns:
        빈 데이터
    """
    # TODO: Implement update will solve problems logic
    # 1. Validate problem IDs
    # 2. Update will solve problems for the date

    return ApiResponse(data={})


@router.post("/problems/solved-problems", response_model=ApiResponseSchema[dict])
@inject
async def update_solved_problems(
    request: UpdateSolvedProblemsRequest,
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    풀었던 문제 업데이트 (날짜 단위)

    Args:
        request: 날짜, 문제 ID 목록

    Returns:
        빈 데이터
    """
    # TODO: Implement update solved problems logic
    # 1. Validate problem IDs
    # 2. Update solved problems for the date

    return ApiResponse(data={})


@router.post("/problems/record", response_model=ApiResponseSchema[dict])
@inject
async def create_or_update_problem_record(
    request: ProblemRecordRequest,
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    문제 기록 생성/업데이트

    Args:
        request: 문제 ID, 메모 제목, 내용

    Returns:
        빈 데이터
    """
    # TODO: Implement create or update problem record logic
    # 1. Check if record exists
    # 2. Create or update record

    return ApiResponse(data={})


@router.get("/problems/record/{problem_id}", response_model=ApiResponseSchema[ProblemRecordResponse])
@inject
async def get_problem_record(
    problem_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    본인의 문제 기록 조회

    Args:
        problem_id: 문제 번호

    Returns:
        문제 기록
    """
    # TODO: Implement get problem record logic
    # 1. Get problem record for current user

    response_data = ProblemRecordResponse(
        memoTitle="메모 제목",
        content="내용"
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))


@router.post("/problems/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def ban_problem(
    request: BanProblemRequest,
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    문제 밴

    Args:
        request: 문제 ID

    Returns:
        빈 데이터
    """
    # TODO: Implement ban problem logic
    # 1. Add problem to banned list

    return ApiResponse(data={})


@router.delete("/problems/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def unban_problem(
    problem_id: int = Query(..., alias="problemId", description="문제 ID"),
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    문제 밴 해제

    Args:
        problem_id: 문제 ID

    Returns:
        빈 데이터
    """
    # TODO: Implement unban problem logic
    # 1. Remove problem from banned list

    return ApiResponse(data={})


@router.post("/tags/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def ban_tag(
    request: BanTagRequest,
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    태그 밴

    Args:
        request: 태그 코드

    Returns:
        빈 데이터
    """
    # TODO: Implement ban tag logic
    # 1. Add tag to banned list

    return ApiResponse(data={})


@router.delete("/tags/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def unban_tag(
    tag_code: str = Query(..., alias="tagCode", description="태그 코드"),
    current_user: CurrentUser = Depends(get_current_member),
    # activity_service = Depends(Provide[Container.activity_service])
):
    """
    태그 밴 해제

    Args:
        tag_code: 태그 코드

    Returns:
        빈 데이터
    """
    # TODO: Implement unban tag logic
    # 1. Remove tag from banned list

    return ApiResponse(data={})
