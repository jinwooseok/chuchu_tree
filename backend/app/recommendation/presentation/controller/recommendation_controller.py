from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide
from typing import List

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.recommendation.presentation.schema.response.recommendation_response import (
    RecommendationResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/user-accounts/me", tags=["recommendation"])


@router.get("/problems", response_model=ApiResponseSchema[RecommendationResponse])
@inject
async def get_recommended_problems(
    level: str = Query(..., description="난이도 필터 (예: ['EASY'])"),
    tags: str = Query(..., description="태그 필터 (예: [])"),
    current_user: CurrentUser = Depends(get_current_member),
    # recommendation_service = Depends(Provide[Container.recommendation_service])
):
    """
    문제 추천 API

    Args:
        level: 난이도 필터 (JSON array string)
        tags: 태그 필터 (JSON array string)

    Returns:
        추천 문제 목록
    """
    # TODO: Implement problem recommendation logic
    # 1. Parse level and tags filters
    # 2. Get user's skill level and targets
    # 3. Recommend problems based on:
    #    - IM_LEVEL: 중급(IM) 레벨 태그 문제
    #    - LEVEL_UP_SOON: 레벨업이 임박한 태그
    #    - LAST_SOLVED_DATE: 오래된 풀이 날짜
    # 4. Filter by user's banned problems and tags

    response_data = RecommendationResponse(problems=[])

    return ApiResponse(data=response_data.model_dump(by_alias=True))
