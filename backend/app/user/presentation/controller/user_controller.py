from fastapi import APIRouter, Depends, UploadFile, File, Query
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.user.application.command.get_tag_problems_command import GetTagProblemsCommand
from app.user.application.command.get_user_tags_command import GetUserTagsCommand
from app.user.application.command.update_user_target_command import UpdateUserTargetCommand
from app.user.application.service.user_account_application_service import UserAccountApplicationService
from app.user.application.usecase.get_tag_problems_usecase import GetTagProblemsUsecase
from app.user.application.usecase.get_user_tags_usecase import GetUserTagsUsecase
from app.user.presentation.schema.request.user_target_request import UpdateUserTargetRequest
from app.user.presentation.schema.response.get_tag_problems_response import GetTagProblemsResponse
from app.user.presentation.schema.response.user_response import (
    ProfileImageResponse,
    AdminUserAccountsResponse
)
from app.user.presentation.schema.response.user_tag_response import TargetResponse, UserTagsResponse
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/user-accounts", tags=["user-accounts"])


@router.post("/profile-image", response_model=ApiResponseSchema[ProfileImageResponse])
@inject
async def set_profile_image(
    profile_image: UploadFile = File(...),
    current_user: CurrentUser = Depends(get_current_member),
    # user_service = Depends(Provide[Container.user_service])
):
    """
    프로필 사진 설정

    Args:
        profile_image: 프로필 이미지 파일 (multipart/form-data)

    Returns:
        프로필 이미지 URL
    """
    # TODO: Implement profile image upload logic
    # 1. Validate image file
    # 2. Upload to storage (MinIO)
    # 3. Update user account

    response_data = ProfileImageResponse(
        profileImageUrl="https://example.com/profile.jpg"
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))


@router.delete("/profile-image", response_model=ApiResponseSchema[dict])
@inject
async def delete_profile_image(
    current_user: CurrentUser = Depends(get_current_member),
    # user_service = Depends(Provide[Container.user_service])
):
    """
    프로필 사진 제거

    Returns:
        빈 데이터
    """
    # TODO: Implement profile image deletion logic
    # 1. Remove image from storage
    # 2. Update user account

    return ApiResponse(data={})


# Admin endpoints
admin_router = APIRouter(prefix="/admin/user-accounts", tags=["admin-user-accounts"])


@admin_router.get("", response_model=ApiResponseSchema[AdminUserAccountsResponse])
@inject
async def get_all_user_accounts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    current_user: CurrentUser = Depends(get_current_member),
    # user_service = Depends(Provide[Container.user_service])
):
    """
    모든 유저 계정 조회 (ADMIN)

    Args:
        page: 페이지 번호 (1부터 시작)

    Returns:
        유저 계정 목록 (페이지네이션)
    """
    # TODO: Implement admin user accounts list logic
    # 1. Check admin permission
    # 2. Get paginated user accounts

    response_data = AdminUserAccountsResponse(
        currentPage=page,
        size=10,
        totalPage=2,
        totalCount=20,
        userAccounts=[]
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))


@router.get("/me/tags/problems", response_model=ApiResponseSchema[GetTagProblemsResponse])
@inject
async def get_tag_problems(
    code: str = Query(..., description="태그 코드"),
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetTagProblemsUsecase = Depends(Provide[Container.get_tag_problems_usecase]),
):
    """
    태그 별 푼 문제 조회

    Args:
        code: 태그 코드

    Returns:
        해당 태그의 유저 푼 문제 목록 (solved_date 포함)
    """
    command = GetTagProblemsCommand(user_account_id=current_user.user_account_id, tag_code=code)
    query = await usecase.execute(command)
    response_data = GetTagProblemsResponse.from_query(query)
    return ApiResponse(data=response_data.model_dump(by_alias=True))


@router.get("/me/tags", response_model=ApiResponseSchema[UserTagsResponse])
@inject
async def get_user_tags(
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetUserTagsUsecase = Depends(Provide[Container.get_user_tags_usecase])
):
    """
    유저의 태그 목록 조회 (카테고리별 분류 + 상세 정보)

    Returns:
        유저의 모든 태그 정보 (EXCLUDED 제외)
    """
    command = GetUserTagsCommand(user_account_id=current_user.user_account_id)
    query = await usecase.execute(command)

    # Query를 Response로 변환 (from_query 사용)
    response_data = UserTagsResponse.from_query(query)

    return ApiResponse(data=response_data.model_dump(by_alias=True))

@router.get("/me/targets", response_model=ApiResponseSchema[UserTagsResponse])
@inject
async def get_user_targets(
    current_user: CurrentUser = Depends(get_current_member),
    user_account_application_service: UserAccountApplicationService = Depends(Provide[Container.user_account_application_service])
):
    """
    유저의 목표 조회

    Returns:
        유저의 목표 조회
    """
    query = await user_account_application_service.get_user_target(current_user.user_account_id)

    # Query를 Response로 변환 (from_query 사용)
    response_data = TargetResponse.from_query(query)

    return ApiResponse(data=response_data.model_dump(by_alias=True))

@router.post("/me/targets", response_model=ApiResponseSchema[UserTagsResponse])
@inject
async def update_user_target(
    request: UpdateUserTargetRequest,
    current_user: CurrentUser = Depends(get_current_member),
    user_account_application_service: UserAccountApplicationService = Depends(Provide[Container.user_account_application_service])
):
    """
    유저의 목표 변경

    Returns:
    
    """
    await user_account_application_service.update_user_target(UpdateUserTargetCommand(user_account_id=current_user.user_account_id, 
                                                                                target_code=request.target_code))

    return ApiResponse(data={})