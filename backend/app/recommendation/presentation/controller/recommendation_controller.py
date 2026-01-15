from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide
from typing import List, Optional
import json

from app.common.domain.enums import FilterCode
from app.common.domain.vo.current_user import CurrentUser
from app.common.domain.vo.identifiers import TagId, UserAccountId
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.recommendation.application.usecase.recommend_problems_usecase import RecommendProblemsUsecase
from app.recommendation.presentation.schema.response.recommendation_response import (
    RecommendationResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/user-accounts/me", tags=["recommendation"])


@router.get("/problems", response_model=ApiResponseSchema[RecommendationResponse])
@inject
async def get_recommended_problems(
    level: Optional[str] = Query("[]", description="난이도 필터 (예: [\"EASY\", \"NORMAL\"])"),
    tags: Optional[str] = Query("[]", description="태그 필터 (예: [1, 2, 3])"),
    count: Optional[int] = Query(3, description="문제 개수"),
    current_user: CurrentUser = Depends(get_current_member),
    recommendation_usecase: RecommendProblemsUsecase = Depends(Provide[Container.recommand_problems_usecase])
):
    """
    문제 추천 API

    Args:
        level: 난이도 필터 (JSON array string, 예: ["EASY", "NORMAL"])
        tags: 태그 필터 (JSON array string, 예: [1, 2, 3])

    Returns:
        추천 문제 목록
    """
    # 1. Query 파라미터 파싱 및 VO 변환
    level_filter_codes: list[FilterCode] | None = None
    if level:
        level_codes = json.loads(level)
        level_filter_codes = [FilterCode(code) for code in level_codes]

    tag_filter_codes: list[TagId] | None = None
    if tags:
        tag_filter_codes = json.loads(tags)

    # 2. Usecase 실행 (Query 객체 반환)
    query = await recommendation_usecase.execute(
        user_account_id=UserAccountId(current_user.user_account_id),
        level_filter_codes=level_filter_codes,
        tag_filter_codes=tag_filter_codes,
        count=count
    )

    # 3. Response 변환
    response_data = RecommendationResponse.from_query(query)

    return ApiResponse(data=response_data)
