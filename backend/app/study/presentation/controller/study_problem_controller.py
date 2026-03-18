import asyncio

from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from dependency_injector.wiring import inject, Provide
from typing import Optional
import json

from app.common.domain.enums import FilterCode, ExclusionMode
from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
from app.study.infra.sse.study_sse_manager import StudySSEManager
from app.recommendation.application.usecase.get_study_recommendation_history_usecase import GetStudyRecommendationHistoryUsecase
from app.recommendation.presentation.schema.response.recommendation_history_response import RecommendationHistoryResponse
from app.study.application.command.study_command import (
    AssignStudyProblemAllCommand,
    AssignStudyProblemCommand,
    DeleteStudyProblemCommand,
    GetStudyProblemsCommand,
    MemberAssignment,
    RecommendStudyProblemsCommand,
)
from app.study.application.usecase.assign_study_problem_all_usecase import AssignStudyProblemAllUsecase
from app.study.application.usecase.assign_study_problem_usecase import AssignStudyProblemUsecase
from app.study.application.usecase.delete_study_problem_usecase import DeleteStudyProblemUsecase
from app.study.application.usecase.get_study_problems_usecase import GetStudyProblemsUsecase
from app.study.application.usecase.recommend_study_problems_usecase import RecommendStudyProblemsUsecase
from app.study.application.usecase.validate_study_member_usecase import ValidateStudyMemberUsecase
from app.study.presentation.schema.request.study_request import (
    AssignStudyProblemAllRequest,
    AssignStudyProblemRequest,
)
from app.study.presentation.schema.response.study_problem_response import StudyProblemsResponse
from app.study.presentation.schema.response.study_recommend_response import StudyRecommendationResponse

study_problem_router = APIRouter(tags=["study-problems"])


@study_problem_router.post("/studies/{study_id}/problems/all", response_model=ApiResponseSchema[None])
@inject
async def assign_study_problem_all(
    study_id: int,
    request: AssignStudyProblemAllRequest,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: AssignStudyProblemAllUsecase = Depends(Provide[Container.assign_study_problem_all_usecase]),
):
    await usecase.execute(AssignStudyProblemAllCommand(
        study_id=study_id,
        problem_id=request.problem_id,
        target_date=request.target_date,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@study_problem_router.post("/studies/{study_id}/problems", response_model=ApiResponseSchema[None])
@inject
async def assign_study_problem(
    study_id: int,
    request: AssignStudyProblemRequest,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: AssignStudyProblemUsecase = Depends(Provide[Container.assign_study_problem_usecase]),
):
    assignments = [
        MemberAssignment(user_account_id=a.user_account_id, target_date=a.target_date)
        for a in request.assignments
    ]
    await usecase.execute(AssignStudyProblemCommand(
        study_id=study_id,
        problem_id=request.problem_id,
        assignments=assignments,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@study_problem_router.delete("/studies/{study_id}/problems/{study_problem_id}", response_model=ApiResponseSchema[None])
@inject
async def delete_study_problem(
    study_id: int,
    study_problem_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: DeleteStudyProblemUsecase = Depends(Provide[Container.delete_study_problem_usecase]),
):
    await usecase.execute(DeleteStudyProblemCommand(
        study_id=study_id,
        study_problem_id=study_problem_id,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@study_problem_router.get("/studies/{study_id}/problems", response_model=ApiResponseSchema[StudyProblemsResponse])
@inject
async def get_study_problems(
    study_id: int,
    year: int = Query(...),
    month: int = Query(...),
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetStudyProblemsUsecase = Depends(Provide[Container.get_study_problems_usecase]),
):
    query = await usecase.execute(GetStudyProblemsCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        year=year,
        month=month,
    ))
    return ApiResponse(data=StudyProblemsResponse.from_query(query).model_dump(by_alias=True))


@study_problem_router.get("/studies/{study_id}/recommend-problems", response_model=ApiResponseSchema[StudyRecommendationResponse])
@inject
async def recommend_study_problems(
    study_id: int,
    target_user_account_id: Optional[int] = Query(default=None),
    level: Optional[str] = Query("[]", description="난이도 필터 (예: [\"EASY\", \"NORMAL\"])"),
    tags: Optional[str] = Query("[]", description="태그 필터 (예: [1, 2, 3])"),
    count: int = Query(default=3),
    exclusion_mode: Optional[str] = Query("LENIENT", description="제외 모드 (LENIENT|STRICT)"),
    recommend_all_unsolved: bool = Query(default=False),
    current_user: CurrentUser = Depends(get_current_member),
    usecase: RecommendStudyProblemsUsecase = Depends(Provide[Container.recommend_study_problems_usecase]),
):
    level_filter_codes: list[FilterCode] | None = None
    if level:
        level_codes = json.loads(level)
        level_filter_codes = [FilterCode(code) for code in level_codes]

    tag_filter_codes: list | None = None
    if tags:
        tag_filter_codes = json.loads(tags)

    exclusion_mode_enum = ExclusionMode(exclusion_mode) if exclusion_mode else ExclusionMode.LENIENT

    query = await usecase.execute(RecommendStudyProblemsCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        target_user_account_id=target_user_account_id,
        level_filter_codes=level_filter_codes,
        tag_filter_codes=tag_filter_codes,
        exclusion_mode=exclusion_mode_enum,
        recommend_all_unsolved=recommend_all_unsolved,
        count=count,
    ))

    return ApiResponse(data=StudyRecommendationResponse.from_query(query))


@study_problem_router.get("/studies/{study_id}/recommend-history", response_model=ApiResponseSchema[RecommendationHistoryResponse])
@inject
async def get_study_recommendation_history(
    study_id: int,
    user_account_id: Optional[int] = Query(default=None),
    page: int = Query(default=1, ge=1, description="페이지 번호 (1부터 시작)"),
    size: int = Query(default=10, ge=1, description="한 페이지 항목 수"),
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetStudyRecommendationHistoryUsecase = Depends(Provide[Container.get_study_recommendation_history_usecase]),
):
    query = await usecase.execute(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        user_account_id=user_account_id,
        page=page,
        size=size,
    )
    return ApiResponse(data=RecommendationHistoryResponse.from_query(query).model_dump(by_alias=True))


@study_problem_router.get("/studies/{study_id}/stream")
@inject
async def study_stream(
    study_id: int,
    current_user: CurrentUser = Depends(get_current_member),
    study_sse_manager: StudySSEManager = Depends(Provide[Container.study_sse_manager]),
    validate_usecase: ValidateStudyMemberUsecase = Depends(Provide[Container.validate_study_member_usecase]),
):
    await validate_usecase.execute(study_id, current_user.user_account_id)

    async def event_generator():
        q = study_sse_manager.connect(study_id, current_user.user_account_id)
        try:
            yield f"data: {json.dumps({'eventType': 'CONNECTED', 'data': {}}, ensure_ascii=False)}\n\n"
            while True:
                try:
                    data = await asyncio.wait_for(q.get(), timeout=30)
                    yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            study_sse_manager.disconnect(study_id, current_user.user_account_id, q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
