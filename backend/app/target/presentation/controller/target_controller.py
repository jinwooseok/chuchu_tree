from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.target.application.service.target_application_service import TargetApplicationService
from app.target.presentation.schema.request.target_request import SetTargetRequest
from app.target.presentation.schema.response.target_response import (
    AllTargetsResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/targets", tags=["targets"])

@router.get("", response_model=ApiResponseSchema[AllTargetsResponse])
@inject
async def get_all_targets(
    target_application_service: TargetApplicationService = Depends(Provide[Container.target_application_service])
):
    """
    모든 목표 조회 (인증 불필요)

    Returns:
        모든 목표 목록
    """
    queries = target_application_service.get_all_targets()
    response_data = AllTargetsResponse.from_queries(queries)

    return ApiResponse(data=response_data.model_dump(by_alias=True))
