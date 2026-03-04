import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from dependency_injector.wiring import inject, Provide

from app.common.domain.vo.current_user import CurrentUser
from app.common.presentation.dependency.auth_dependencies import get_current_member
from app.core.api_response import ApiResponse, ApiResponseSchema
from app.core.containers import Container
from app.study.application.command.study_command import GetMyNoticesCommand, MarkNoticesReadCommand
from app.study.application.usecase.get_my_notices_usecase import GetMyNoticesUsecase
from app.study.application.usecase.mark_notices_read_usecase import MarkNoticesReadUsecase
from app.study.infra.sse.notice_manager import NoticeSSEManager
from app.study.presentation.schema.request.study_request import MarkNoticesReadRequest
from app.study.presentation.schema.response.notice_response import MyNoticesResponse

notice_router = APIRouter(tags=["notices"])


@notice_router.get("/user-accounts/me/notices", response_model=ApiResponseSchema[MyNoticesResponse])
@inject
async def get_my_notices(
    current_user: CurrentUser = Depends(get_current_member),
    usecase: GetMyNoticesUsecase = Depends(Provide[Container.get_my_notices_usecase]),
):
    queries = await usecase.execute(GetMyNoticesCommand(
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=MyNoticesResponse.from_query(queries).model_dump(by_alias=True))


@notice_router.patch("/user-accounts/me/notices/read", response_model=ApiResponseSchema[None])
@inject
async def mark_notices_read(
    request: MarkNoticesReadRequest,
    current_user: CurrentUser = Depends(get_current_member),
    usecase: MarkNoticesReadUsecase = Depends(Provide[Container.mark_notices_read_usecase]),
):
    await usecase.execute(MarkNoticesReadCommand(
        notice_ids=request.notice_ids,
        requester_user_account_id=current_user.user_account_id,
    ))
    return ApiResponse(data=None)


@notice_router.get("/user-accounts/me/notices/stream")
@inject
async def notice_stream(
    current_user: CurrentUser = Depends(get_current_member),
    notice_sse_manager: NoticeSSEManager = Depends(Provide[Container.notice_sse_manager]),
):
    async def event_generator():
        q = notice_sse_manager.connect(current_user.user_account_id)
        try:
            yield "data: connected\n\n"
            while True:
                data = await q.get()
                yield f"data: {json.dumps(data, ensure_ascii=False)}\n\n"
        finally:
            notice_sse_manager.disconnect(current_user.user_account_id, q)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
