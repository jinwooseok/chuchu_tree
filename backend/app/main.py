import os
from datetime import datetime
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from fastapi.concurrency import asynccontextmanager

from app.core.api_response import ApiResponse
from app.core.containers import Container
from app.core.loggers import setup_logging
from app.core import database
import app.core.database_models
from app.core.exception import (
    APIException,
    custom_exception_handler,
    http_exception_handler,
    validation_exception_handler
)
from app.middlewares import create_middlewares

# Import routers
from app.common.presentation.controller.auth_controller import router as auth_router
from app.user.presentation.controller.user_controller import router as user_router, admin_router as admin_user_router
from app.baekjoon.presentation.controller.baekjoon_controller import router as baekjoon_router
from app.target.presentation.controller.target_controller import (
    router as target_router
)
from app.activity.presentation.controller.activity_controller import router as activity_router
from app.problem.presentation.controller.problem_controller import router as problem_router
from app.tag.presentation.controller.tag_controller import router as tag_router, user_router as tag_user_router
from app.recommendation.presentation.controller.recommendation_controller import router as recommendation_router

setup_logging()

class AppWithContainer(FastAPI):
    """Container를 포함한 FastAPI 앱 클래스"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container: Container | None = None

@asynccontextmanager
async def lifespan(app: AppWithContainer):
    injection_container = Container()
    app.container = injection_container
    await injection_container.init_resources_provider(injection_container)
    try:
        yield
    finally:
        # Shutdown: 정리 작업
        db = injection_container.database()

app = AppWithContainer(
    title="ChuChuTree API",
    description="FastAPI 서버 API",
    version="1.0.0",
    openapi_url="/api/v1/openapi.json",   # OpenAPI 스펙 문서 경로
    docs_url="/api/v1/docs",             # Swagger UI 경로
    redoc_url="/api/v1/redoc",           # ReDoc 경로
    default_response_class=ApiResponse,
    lifespan=lifespan
)

# Register middlewares (CORS 등)
create_middlewares(app)

# Prometheus metrics (미들웨어 이후에 등록)
from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

# Register exception handlers
app.add_exception_handler(APIException, custom_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Register routers with /api/v1 prefix
API_V1_PREFIX = "/api/v1"

# Auth routers
app.include_router(auth_router, prefix=API_V1_PREFIX)

# User routers
app.include_router(user_router, prefix=API_V1_PREFIX)
app.include_router(admin_user_router, prefix=API_V1_PREFIX)

# Baekjoon routers
app.include_router(baekjoon_router, prefix=API_V1_PREFIX)

# Target routers
app.include_router(target_router, prefix=API_V1_PREFIX)

# Activity router
app.include_router(activity_router, prefix=API_V1_PREFIX)

# Problem router
app.include_router(problem_router, prefix=API_V1_PREFIX)

# Tag routers
app.include_router(tag_router, prefix=API_V1_PREFIX)
app.include_router(tag_user_router, prefix=API_V1_PREFIX)

# Recommendation router
app.include_router(recommendation_router, prefix=API_V1_PREFIX)

# Test auth router (local/dev 환경에서만 등록, prod에서는 비활성화)
if os.getenv("environment", "local") != "prod":
    from app.common.presentation.controller.test_auth_controller import router as test_auth_router
    app.include_router(test_auth_router, prefix=API_V1_PREFIX)

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",
                host="localhost",
                port=8000,
                reload=True, # 개발버전용 reload=True / 배포버전은 False
                log_config=None # uvicorn 기본 로깅 비활성화
) 