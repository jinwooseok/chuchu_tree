from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
from app.study.application.command.study_command import (
    GetMyStudiesCommand,
    KickStudyMemberCommand,
    LeaveStudyCommand,
)
from app.study.application.usecase.get_my_studies_usecase import GetMyStudiesUsecase
from app.study.application.usecase.kick_study_member_usecase import KickStudyMemberUsecase
from app.study.application.usecase.leave_study_usecase import LeaveStudyUsecase
from app.study.presentation.schema.response.study_response import MyStudiesResponse

member_router = APIRouter(tags=["study-members"])


@member_router.get("/user-accounts/me/studies", response_model=ApiResponseSchema[MyStudiesResponse])
@inject
async def get_my_studies(
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetMyStudiesUsecase = Depends(Provide[Container.get_my_studies_usecase]),
):
    queries = await usecase.execute(GetMyStudiesCommand(
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=MyStudiesResponse.from_query(queries).model_dump(by_alias=True))


@member_router.post("/studies/{study_id}/members/leave", response_model=ApiResponseSchema[None])
@inject
async def leave_study(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: LeaveStudyUsecase = Depends(Provide[Container.leave_study_usecase]),
):
    await usecase.execute(LeaveStudyCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@member_router.delete("/studies/{study_id}/members/{member_user_account_id}", response_model=ApiResponseSchema[None])
@inject
async def kick_study_member(
    study_id: int,
    member_user_account_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: KickStudyMemberUsecase = Depends(Provide[Container.kick_study_member_usecase]),
):
    await usecase.execute(KickStudyMemberCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        target_user_account_id=member_user_account_id,
    ))
    return ApiResponse(data=None)
