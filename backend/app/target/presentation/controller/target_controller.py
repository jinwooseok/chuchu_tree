from fastapi import APIRouter, Depends
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.target.presentation.schema.request.target_request import SetTargetRequest
from app.target.presentation.schema.response.target_response import (
    UserTargetsResponse,
    AllTargetsResponse
)
from app.core.containers import Container
from app.core.api_response import ApiResponse, ApiResponseSchema

router = APIRouter(prefix="/targets", tags=["user-targets"])

@router.get("", response_model=ApiResponseSchema[AllTargetsResponse])
@inject
async def get_all_targets(
    target_application_service = Depends(Provide[Container.target_application_service])
):
    """
    모든 목표 조회 (인증 불필요)

    Returns:
        모든 목표 목록
    """
    # TODO: Implement get all targets logic
    # 1. Get all available targets
    query = target_application_service.get_all_targets()
    response_data = AllTargetsResponse.from_query()

    return ApiResponse(data=response_data.model_dump(by_alias=True))
