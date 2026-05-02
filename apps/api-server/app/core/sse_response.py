from collections.abc import AsyncGenerator

from fastapi.responses import StreamingResponse

_SSE_HEADERS = {
    "Cache-Control": "no-cache",
    "X-Accel-Buffering": "no",
    "Connection": "keep-alive",
}


def SseStreamingResponse(generator: AsyncGenerator) -> StreamingResponse:
    """SSE 응답 공통 헬퍼. X-Accel-Buffering: no 포함."""
    return StreamingResponse(
        generator,
        media_type="text/event-stream",
        headers=_SSE_HEADERS,
    )
