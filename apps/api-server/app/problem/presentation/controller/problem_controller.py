from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.problem.application.query.problems_info_query import ProblemsInfoQuery
from app.problem.application.service.problem_application_service import ProblemApplicationService
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
    problem_application_service: ProblemApplicationService = Depends(Provide[Container.problem_application_service])
):
    """
    문제 검색 (문제 이름, ID 각 5개)

    Args:
        keyword: 검색 키워드

    Returns:
        ID 기반 검색 결과 (최대 5개)
        제목 기반 검색 결과 (최대 5개)
    """
    
    queries: list[ProblemsInfoQuery] = await problem_application_service.search_problem_by_keyword(keyword)

    response_data = ProblemSearchResponse.from_queries(queries[0], queries[1])

    return ApiResponse(data=response_data.model_dump(by_alias=True))
