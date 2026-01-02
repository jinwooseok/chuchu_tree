from fastapi import APIRouter, Query
from dependency_injector.wiring import inject, Provide

from app.problem.presentation.schema.response.problem_response import (
    ProblemSearchResponse,
    ProblemSearchResults
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/problems", tags=["problems"])


@router.get("/search", response_model=ApiResponseSchema[ProblemSearchResponse])
@inject
async def search_problems(
    keyword: str = Query(..., description="검색 키워드"),
    # problem_service = Depends(Provide[Container.problem_service])
):
    """
    문제 검색 (문제 이름, ID 각 5개)

    Args:
        keyword: 검색 키워드

    Returns:
        ID 기반 검색 결과 (최대 5개)
        제목 기반 검색 결과 (최대 5개)
    """
    # TODO: Implement problem search logic
    # 1. Search problems by ID (if keyword is numeric)
    # 2. Search problems by title
    # 3. Return up to 5 results for each

    response_data = ProblemSearchResponse(
        problems=ProblemSearchResults(
            idBaseTotalCount=0,
            titleBaseTotalCount=0,
            idBase=[],
            titleBase=[]
        )
    )

    return ApiResponse(data=response_data.model_dump(by_alias=True))
