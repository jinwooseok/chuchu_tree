from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.tag.presentation.schema.response.tag_response import (
    UserTagsResponse,
    AllTagsResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

# User tag endpoints
user_router = APIRouter(prefix="/user-accounts/me", tags=["user-tags"])


@user_router.get("/tags", response_model=ApiResponseSchema[UserTagsResponse])
@inject
async def get_user_tags(
    current_user: CurrentUser = Depends(get_current_member),
    # tag_service = Depends(Provide[Container.tag_service])
):
    """
    유저의 태그 목록 조회 (EXCLUDED - 유저 밴 + 목표 포함 X)

    Returns:
        카테고리별 태그, 전체 태그 목록
    """
    # TODO: Implement get user tags logic
    # 1. Get all tags
    # 2. Filter by user's ban list
    # 3. Filter by user's targets
    # 4. Calculate statistics for each tag

    response_data = UserTagsResponse(
        categories=[],
        tags=[]
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))


# Public tag endpoints
router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("", response_model=ApiResponseSchema[AllTagsResponse])
@inject
async def get_all_tags(
    # tag_service = Depends(Provide[Container.tag_service])
):
    """
    전체 태그 목록 조회 (인증 불필요)

    Returns:
        전체 태그 목록
    """
    # TODO: Implement get all tags logic
    # 1. Get all tags with level stats

    response_data = AllTagsResponse(tags=[])

    return ApiResponse(data=response_data.model_dump(by_alias=True))
