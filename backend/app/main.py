from datetime import datetime
from fastapi import FastAPI

from fastapi.concurrency import asynccontextmanager

from app.core.api_response import ApiResponse
from app.core.containers import Container
from app.core.loggers import setup_logging

setup_logging()

class AppWithContainer(FastAPI):
    """Container를 포함한 FastAPI 앱 클래스"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.container: Container|None = None

@asynccontextmanager
async def lifespan(app: AppWithContainer):
    injection_container = Container()
    app.container = injection_container
    db = injection_container.db()
    # core.database.database_instance = db
    try:
        yield
    finally:
        # 정리 작업
        return

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

@app.get("/health")
async def health_check():
    """헬스체크 엔드포인트"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app",
                host="127.0.0.1",
                port=8080,
                reload=True, # 개발버전용 reload=True / 배포버전은 False
                log_config=None # uvicorn 기본 로깅 비활성화
)