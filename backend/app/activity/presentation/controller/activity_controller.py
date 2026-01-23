from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.activity.application.command.ban_problem_command import BanProblemCommand
from app.activity.application.command.set_representative_tag_command import (
    SetSolvedProblemRepresentativeTagCommand,
    SetWillSolveProblemRepresentativeTagCommand
)
from app.activity.application.command.tag_custom_command import TagCustomCommand
from app.activity.application.command.update_solved_problems_command import UpdateSolvedProblemsCommand
from app.activity.application.command.update_solved_will_solve_problems_command import UpdateSolvedAndWillSolveProblemsCommand
from app.activity.application.command.update_will_solve_problems import UpdateWillSolveProblemsCommand
from app.activity.application.query.banned_list_query import BannedProblemsQuery
from app.activity.application.service.activity_application_service import ActivityApplicationService
from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.activity.presentation.schema.request.activity_request import (
    UpdateSolvedAndWillSolveProblemsRequest,
    UpdateWillSolveProblemsRequest,
    UpdateSolvedProblemsRequest,
    ProblemRecordRequest,
    BanProblemRequest,
    BanTagRequest,
    SetRepresentativeTagRequest
)
from app.activity.presentation.schema.response.activity_response import (
    BannedProblemsResponse,
    BannedTagsResponse,
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
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    풀 문제 업데이트 (날짜 단위)

    Args:
        request: 날짜, 문제 ID 목록

    Returns:
        빈 데이터
    """
    await activity_application_service.update_will_solve_problems(UpdateWillSolveProblemsCommand(user_account_id = current_user.user_account_id, 
                                                                                              solved_date = request.date, 
                                                                                              problem_ids = request.problem_ids))

    return ApiResponse(data={})


@router.post("/problems/solved-problems", response_model=ApiResponseSchema[dict])
@inject
async def update_solved_problems(
    request: UpdateSolvedProblemsRequest,
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    풀었던 문제 업데이트 (날짜 단위)

    Args:
        request: 날짜, 문제 ID 목록

    Returns:
        빈 데이터
    """
    await activity_application_service.update_solved_problems(UpdateSolvedProblemsCommand(user_account_id = current_user.user_account_id, 
                                                                                              solved_date = request.date, 
                                                                                              problem_ids = request.problem_ids))

    return ApiResponse(data={})

@router.post("/problems/solved-and-will-solve-problems", response_model=ApiResponseSchema[dict])
@inject
async def update_solved_and_will_solve_problems(
    request: UpdateSolvedAndWillSolveProblemsRequest,
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    풀었던 문제, 풀 문제 동시 업데이트

    Args:
        request: 날짜, 문제 ID 목록

    Returns:
        빈 데이터
    """
    await activity_application_service.update_solved_and_will_solve_problems(UpdateSolvedAndWillSolveProblemsCommand(user_account_id = current_user.user_account_id, 
                                                                                              solved_date = request.date, 
                                                                                              solved_problem_ids = request.solved_problem_ids,
                                                                                              will_solve_problem_ids= request.will_solve_problem_ids))

    return ApiResponse(data={})


@router.post("/problems/record", response_model=ApiResponseSchema[dict])
@inject
async def create_or_update_problem_record(
    request: ProblemRecordRequest,
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    문제 기록 생성/업데이트

    Args:
        request: 문제 ID, 메모 제목, 내용

    Returns:
        빈 데이터
    """
    
    # await activity_application_service.create_problem_record()
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
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    문제 밴

    Args:
        request: 문제 ID

    Returns:
        빈 데이터
    """
    
    await activity_application_service.ban_problem(BanProblemCommand(user_account_id=current_user.user_account_id, 
                                                                     problem_id=request.problem_id,
                                                                     problem_ban_yn=False))
    return ApiResponse(data={})


@router.delete("/problems/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def unban_problem(
    problem_id: int = Query(..., alias="problemId", description="문제 ID"),
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    문제 밴 해제

    Args:
        problem_id: 문제 ID

    Returns:
        빈 데이터
    """
    # 1. Remove problem from banned list
    await activity_application_service.unban_problem(BanProblemCommand(user_account_id=current_user.user_account_id, 
                                                                     problem_id=problem_id,
                                                                     problem_ban_yn=False))
    
    return ApiResponse(data={})


@router.post("/tags/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def ban_tag(
    request: BanTagRequest,
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service:ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    태그 밴

    Args:
        request: 태그 코드

    Returns:
        빈 데이터
    """
    await activity_application_service.ban_tag(TagCustomCommand(
            user_account_id=current_user.user_account_id,
            tag_code=request.tag_code,
            tag_ban_yn=True
        )
    )

    return ApiResponse(data={})


@router.delete("/tags/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def unban_tag(
    tag_code: str = Query(..., alias="tagCode", description="태그 코드"),
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service:ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    태그 밴 해제

    Args:
        tag_code: 태그 코드

    Returns:
        빈 데이터
    """
    await activity_application_service.unban_tag(TagCustomCommand(
        user_account_id=current_user.user_account_id,
        tag_code=tag_code,
        tag_ban_yn=False
    ))

    return ApiResponse(data={})

@router.get("/problems/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def get_banned_problems(
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    query: BannedProblemsQuery = await activity_application_service.get_banned_problems(current_user.user_account_id)
    
    return ApiResponse(data=BannedProblemsResponse.from_query(query))

@router.get("/tags/banned-list", response_model=ApiResponseSchema[dict])
@inject
async def get_banned_tags(
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    query = await activity_application_service.get_banned_tags(current_user.user_account_id)

    return ApiResponse(data=BannedTagsResponse.from_query(query))


@router.put("/problems/solved-problems/{problem_id}/representative-tag", response_model=ApiResponseSchema[dict])
@inject
async def set_solved_problem_representative_tag(
    problem_id: int,
    request: SetRepresentativeTagRequest,
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    푼 문제의 대표 태그 설정

    Args:
        problem_id: 문제 ID
        request: 대표 태그 코드 (null이면 대표 태그 해제)

    Returns:
        빈 데이터
    """
    await activity_application_service.set_solved_problem_representative_tag(
        SetSolvedProblemRepresentativeTagCommand(
            user_account_id=current_user.user_account_id,
            problem_id=problem_id,
            representative_tag_code=request.representative_tag_code
        )
    )

    return ApiResponse(data={})


@router.put("/problems/will-solve-problems/{problem_id}/representative-tag", response_model=ApiResponseSchema[dict])
@inject
async def set_will_solve_problem_representative_tag(
    problem_id: int,
    request: SetRepresentativeTagRequest,
    current_user: CurrentUser = Depends(get_current_member),
    activity_application_service: ActivityApplicationService = Depends(Provide[Container.activity_application_service])
):
    """
    풀 예정 문제의 대표 태그 설정

    Args:
        problem_id: 문제 ID
        request: 대표 태그 코드 (null이면 대표 태그 해제)

    Returns:
        빈 데이터
    """
    await activity_application_service.set_will_solve_problem_representative_tag(
        SetWillSolveProblemRepresentativeTagCommand(
            user_account_id=current_user.user_account_id,
            problem_id=problem_id,
            representative_tag_code=request.representative_tag_code
        )
    )

    return ApiResponse(data={})