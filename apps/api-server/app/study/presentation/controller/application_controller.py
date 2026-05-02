from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
from app.study.application.command.study_command import (
    AcceptStudyApplicationCommand,
    ApplyToStudyCommand,
    CancelStudyApplicationCommand,
    GetStudyApplicationsCommand,
    RejectStudyApplicationCommand,
)
from app.study.application.usecase.accept_study_application_usecase import AcceptStudyApplicationUsecase
from app.study.application.usecase.apply_to_study_usecase import ApplyToStudyUsecase
from app.study.application.usecase.cancel_study_application_usecase import CancelStudyApplicationUsecase
from app.study.application.usecase.get_study_applications_usecase import GetStudyApplicationsUsecase
from app.study.application.usecase.reject_study_application_usecase import RejectStudyApplicationUsecase
from app.study.presentation.schema.request.study_request import ApplyToStudyRequest
from app.study.presentation.schema.response.application_response import StudyApplicationsResponse

application_router = APIRouter(tags=["study-applications"])


@application_router.post("/studies/{study_id}/applications", response_model=ApiResponseSchema[None])
@inject
async def apply_to_study(
    study_id: int,
    request: ApplyToStudyRequest,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: ApplyToStudyUsecase = Depends(Provide[Container.apply_to_study_usecase]),
):
    await usecase.execute(ApplyToStudyCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        message=request.message,
    ))
    return ApiResponse(data=None)


@application_router.delete("/studies/{study_id}/applications/me", response_model=ApiResponseSchema[None])
@inject
async def cancel_study_application(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: CancelStudyApplicationUsecase = Depends(Provide[Container.cancel_study_application_usecase]),
):
    await usecase.execute(CancelStudyApplicationCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@application_router.get("/studies/{study_id}/applications", response_model=ApiResponseSchema[StudyApplicationsResponse])
@inject
async def get_study_applications(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetStudyApplicationsUsecase = Depends(Provide[Container.get_study_applications_usecase]),
):
    queries = await usecase.execute(GetStudyApplicationsCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=StudyApplicationsResponse.from_query(queries).model_dump(by_alias=True))


@application_router.post("/studies/applications/{application_id}/accept", response_model=ApiResponseSchema[None])
@inject
async def accept_study_application(
    application_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: AcceptStudyApplicationUsecase = Depends(Provide[Container.accept_study_application_usecase]),
):
    await usecase.execute(AcceptStudyApplicationCommand(
        application_id=application_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@application_router.post("/studies/applications/{application_id}/reject", response_model=ApiResponseSchema[None])
@inject
async def reject_study_application(
    application_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: RejectStudyApplicationUsecase = Depends(Provide[Container.reject_study_application_usecase]),
):
    await usecase.execute(RejectStudyApplicationCommand(
        application_id=application_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)
