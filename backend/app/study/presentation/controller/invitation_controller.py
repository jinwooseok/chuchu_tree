from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
from app.study.application.command.study_command import (
    AcceptStudyInvitationCommand,
    CancelStudyInvitationCommand,
    GetMyInvitationsCommand,
    GetMyPendingRequestsCommand,
    GetStudyInvitationsCommand,
    RejectStudyInvitationCommand,
    SendStudyInvitationCommand,
)
from app.study.application.usecase.accept_study_invitation_usecase import AcceptStudyInvitationUsecase
from app.study.application.usecase.cancel_study_invitation_usecase import CancelStudyInvitationUsecase
from app.study.application.usecase.get_my_invitations_usecase import GetMyInvitationsUsecase
from app.study.application.usecase.get_my_pending_requests_usecase import GetMyPendingRequestsUsecase
from app.study.application.usecase.get_study_invitations_usecase import GetStudyInvitationsUsecase
from app.study.application.usecase.reject_study_invitation_usecase import RejectStudyInvitationUsecase
from app.study.application.usecase.send_study_invitation_usecase import SendStudyInvitationUsecase
from app.study.presentation.schema.request.study_request import SendInvitationRequest
from app.study.presentation.schema.response.invitation_response import MyInvitationsResponse, MyPendingRequestsResponse

invitation_router = APIRouter(tags=["study-invitations"])


@invitation_router.get("/studies/{study_id}/invitations", response_model=ApiResponseSchema[MyInvitationsResponse])
@inject
async def get_study_invitations(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetStudyInvitationsUsecase = Depends(Provide[Container.get_study_invitations_usecase]),
):
    queries = await usecase.execute(GetStudyInvitationsCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=MyInvitationsResponse.from_query(queries).model_dump(by_alias=True))


@invitation_router.post("/studies/{study_id}/invitations", response_model=ApiResponseSchema[None])
@inject
async def send_study_invitation(
    study_id: int,
    request: SendInvitationRequest,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: SendStudyInvitationUsecase = Depends(Provide[Container.send_study_invitation_usecase]),
):
    await usecase.execute(SendStudyInvitationCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        invitee_user_account_id=request.invitee_user_account_id,
    ))
    return ApiResponse(data=None)


@invitation_router.delete("/studies/{study_id}/invitations/{invitation_id}", response_model=ApiResponseSchema[None])
@inject
async def cancel_study_invitation(
    study_id: int,
    invitation_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: CancelStudyInvitationUsecase = Depends(Provide[Container.cancel_study_invitation_usecase]),
):
    await usecase.execute(CancelStudyInvitationCommand(
        study_id=study_id,
        invitation_id=invitation_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@invitation_router.get("/user-accounts/me/pending-requests", response_model=ApiResponseSchema[MyPendingRequestsResponse])
@inject
async def get_my_pending_requests(
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetMyPendingRequestsUsecase = Depends(Provide[Container.get_my_pending_requests_usecase]),
):
    invitation_queries, application_queries = await usecase.execute(GetMyPendingRequestsCommand(
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=MyPendingRequestsResponse.from_queries(invitation_queries, application_queries).model_dump(by_alias=True))


@invitation_router.get("/user-accounts/me/invitations", response_model=ApiResponseSchema[MyInvitationsResponse])
@inject
async def get_my_invitations(
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetMyInvitationsUsecase = Depends(Provide[Container.get_my_invitations_usecase]),
):
    queries = await usecase.execute(GetMyInvitationsCommand(
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=MyInvitationsResponse.from_query(queries).model_dump(by_alias=True))


@invitation_router.post("/user-accounts/me/invitations/{invitation_id}/accept", response_model=ApiResponseSchema[None])
@inject
async def accept_study_invitation(
    invitation_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: AcceptStudyInvitationUsecase = Depends(Provide[Container.accept_study_invitation_usecase]),
):
    await usecase.execute(AcceptStudyInvitationCommand(
        invitation_id=invitation_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@invitation_router.post("/user-accounts/me/invitations/{invitation_id}/reject", response_model=ApiResponseSchema[None])
@inject
async def reject_study_invitation(
    invitation_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: RejectStudyInvitationUsecase = Depends(Provide[Container.reject_study_invitation_usecase]),
):
    await usecase.execute(RejectStudyInvitationCommand(
        invitation_id=invitation_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)
