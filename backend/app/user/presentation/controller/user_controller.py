from fastapi import APIRouter, Depends, UploadFile, File, Query
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.user.application.command.get_user_tags_command import GetUserTagsCommand
from app.user.application.usecase.get_user_tags_usecase import GetUserTagsUsecase
from app.user.presentation.schema.response.user_response import (
    ProfileImageResponse,
    AdminUserAccountsResponse
)
from app.user.presentation.schema.response.user_tag_response import UserTagsResponse
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

    # Query를 Response로 변환
    response_data = UserTagsResponse(
        categories=[
            {
                "categoryName": cat.category_name,
                "tags": [
                    {
                        "tagId": tag.tag_id,
                        "tagCode": tag.tag_code,
                        "tagDisplayName": tag.tag_display_name,
                        "tagTargets": [
                            {
                                "targetId": target.target_id,
                                "targetCode": target.target_code,
                                "targetDisplayName": target.target_display_name
                            }
                            for target in tag.tag_targets
                        ],
                        "tagAliases": [{"alias": alias.alias} for alias in tag.tag_aliases],
                        "requiredStat": {
                            "requiredMinTier": tag.required_stat.required_min_tier,
                            "prevTags": [
                                {
                                    "tagId": prev.tag_id,
                                    "tagCode": prev.tag_code,
                                    "tagDisplayName": prev.tag_display_name,
                                    "satisfiedYn": prev.satisfied_yn
                                }
                                for prev in tag.required_stat.prev_tags
                            ]
                        } if tag.required_stat else None,
                        "nextLevelStat": {
                            "nextLevel": tag.next_level_stat.next_level,
                            "solvedProblemCount": tag.next_level_stat.solved_problem_count,
                            "requiredMinTier": tag.next_level_stat.required_min_tier,
                            "higherProblemTier": tag.next_level_stat.higher_problem_tier
                        } if tag.next_level_stat else None,
                        "accountStat": {
                            "currentLevel": tag.account_stat.current_level,
                            "solvedProblemCount": tag.account_stat.solved_problem_count,
                            "requiredMinTier": tag.account_stat.required_min_tier,
                            "higherProblemTier": tag.account_stat.higher_problem_tier,
                            "lastSolvedDate": tag.account_stat.last_solved_date
                        },
                        "lockedYn": tag.locked_yn,
                        "excludedYn": tag.excluded_yn,
                        "recommendationYn": tag.recommendation_yn
                    }
                    for tag in cat.tags
                ]
            }
            for cat in query.categories
        ],
        tags=[
            {
                "tagId": tag.tag_id,
                "tagCode": tag.tag_code,
                "tagDisplayName": tag.tag_display_name,
                "tagTargets": [
                    {
                        "targetId": target.target_id,
                        "targetCode": target.target_code,
                        "targetDisplayName": target.target_display_name
                    }
                    for target in tag.tag_targets
                ],
                "tagAliases": [{"alias": alias.alias} for alias in tag.tag_aliases],
                "requiredStat": {
                    "requiredMinTier": tag.required_stat.required_min_tier,
                    "prevTags": [
                        {
                            "tagId": prev.tag_id,
                            "tagCode": prev.tag_code,
                            "tagDisplayName": prev.tag_display_name,
                            "satisfiedYn": prev.satisfied_yn
                        }
                        for prev in tag.required_stat.prev_tags
                    ]
                } if tag.required_stat else None,
                "nextLevelStat": {
                    "nextLevel": tag.next_level_stat.next_level,
                    "solvedProblemCount": tag.next_level_stat.solved_problem_count,
                    "requiredMinTier": tag.next_level_stat.required_min_tier,
                    "higherProblemTier": tag.next_level_stat.higher_problem_tier
                } if tag.next_level_stat else None,
                "accountStat": {
                    "currentLevel": tag.account_stat.current_level,
                    "solvedProblemCount": tag.account_stat.solved_problem_count,
                    "requiredMinTier": tag.account_stat.required_min_tier,
                    "higherProblemTier": tag.account_stat.higher_problem_tier,
                    "lastSolvedDate": tag.account_stat.last_solved_date
                },
                "lockedYn": tag.locked_yn,
                "excludedYn": tag.excluded_yn,
                "recommendationYn": tag.recommendation_yn
            }
            for tag in query.tags
        ]
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))
