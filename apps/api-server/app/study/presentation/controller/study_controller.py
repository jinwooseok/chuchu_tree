import json
from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member, get_current_member_or_none
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
from app.study.application.command.study_command import (
    CreateStudyCommand,
    DeleteStudyCommand,
    GetStudyDetailCommand,
    SearchStudyCommand,
    UpdateStudyCommand,
    ValidateStudyNameCommand,
)
from app.study.application.usecase.create_study_usecase import CreateStudyUsecase
from app.study.application.usecase.delete_study_usecase import DeleteStudyUsecase
from app.study.application.usecase.get_study_detail_usecase import GetStudyDetailUsecase
from app.study.application.usecase.search_study_usecase import SearchStudyUsecase
from app.study.application.usecase.update_study_usecase import UpdateStudyUsecase
from app.study.application.usecase.validate_study_name_usecase import ValidateStudyNameUsecase
from app.study.presentation.schema.request.study_request import CreateStudyRequest, UpdateStudyRequest
from app.study.presentation.schema.response.study_response import (
    CreateStudyResponse,
    NameAvailableResponse,
    StudyDetailResponse,
    StudySearchResponse,
)

router = APIRouter(prefix="/studies", tags=["studies"])


@router.get("/validate-name", response_model=ApiResponseSchema[NameAvailableResponse])
@inject
async def validate_study_name(
    name: str = Query(...),
    current_user: CurrentUser = Depends(get_current_member),
    usecase: ValidateStudyNameUsecase = Depends(Provide[Container.validate_study_name_usecase]),
):
    query = await usecase.execute(ValidateStudyNameCommand(name=name))
    return ApiResponse(data=NameAvailableResponse.from_query(query).model_dump(by_alias=True))


@router.post("", response_model=ApiResponseSchema[CreateStudyResponse])
@inject
async def create_study(
    request: CreateStudyRequest,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: CreateStudyUsecase = Depends(Provide[Container.create_study_usecase]),
):
    command = CreateStudyCommand(
        requester_user_account_id=current_user.user_account_id,
        study_name=request.study_name,
        description=request.description,
        max_members=request.max_members,
        invitee_user_account_ids=request.invitee_user_account_ids,
    )
    query = await usecase.execute(command)
    return ApiResponse(data=CreateStudyResponse.from_query(query).model_dump(by_alias=True))


@router.get("/search", response_model=ApiResponseSchema[StudySearchResponse])
@inject
async def search_studies(
    keyword: str = Query(...),
    limit: int = Query(5),
    current_user: CurrentUser = Depends(get_current_member),
    usecase: SearchStudyUsecase = Depends(Provide[Container.search_study_usecase]),
):
    queries = await usecase.execute(SearchStudyCommand(keyword=keyword, limit=limit))
    return ApiResponse(data=StudySearchResponse.from_query(queries).model_dump(by_alias=True))


@router.get("/{study_id}", response_model=ApiResponseSchema[StudyDetailResponse])
@inject
async def get_study_detail(
    study_id: int,
    current_user: CurrentUser | None = Depends(get_current_member_or_none),
    usecase: GetStudyDetailUsecase = Depends(Provide[Container.get_study_detail_usecase]),
):
    query = await usecase.execute(GetStudyDetailCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id if current_user else 0,
    ))
    return ApiResponse(data=StudyDetailResponse.from_query(query).model_dump(by_alias=True))


@router.patch("/{study_id}", response_model=ApiResponseSchema[None])
@inject
async def update_study(
    study_id: int,
    request: UpdateStudyRequest,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: UpdateStudyUsecase = Depends(Provide[Container.update_study_usecase]),
):
    await usecase.execute(UpdateStudyCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        description=request.description,
        max_members=request.max_members,
    ))
    return ApiResponse(data=None)


@router.delete("/{study_id}", response_model=ApiResponseSchema[None])
@inject
async def delete_study(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: DeleteStudyUsecase = Depends(Provide[Container.delete_study_usecase]),
):
    await usecase.execute(DeleteStudyCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)
