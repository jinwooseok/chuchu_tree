from fastapi import APIRouter, Depends, Query
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
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
    target_user_account_id: int | None = Query(default=None),
    recommend_all_unsolved: bool = Query(default=False),
    count: int = Query(default=3),
    current_user: CurrentUser = Depends(get_current_member),
    usecase: RecommendStudyProblemsUsecase = Depends(Provide[Container.recommend_study_problems_usecase]),
):
    query = await usecase.execute(RecommendStudyProblemsCommand(
        study_id=study_id,
        requester_user_account_id=current_user.user_account_id,
        target_user_account_id=target_user_account_id,
        recommend_all_unsolved=recommend_all_unsolved,
        count=count,
    ))
    return ApiResponse(data=StudyRecommendationResponse.from_query(query).model_dump(by_alias=True))
