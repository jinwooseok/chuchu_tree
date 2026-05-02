import os
from starlette.types import ASGIApp, Receive, Scope, Send
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.database import get_global_database, reset_database_context, set_database_context

class DatabaseContextMiddleware:
    """요청별로 Database 인스턴스를 ContextVar에 설정 (Pure ASGI 미들웨어)

    BaseHTTPMiddleware 대신 순수 ASGI 미들웨어로 구현.
    BaseHTTPMiddleware의 call_next()는 별도 task에서 실행되어
    ContextVar가 전파되지 않는 문제가 있음.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        # Unit 테스트: DB context 설정 불필요 (@transactional이 완전 우회됨)
        db_session = os.getenv('DB_SESSION', '').lower()
        if db_session == 'unit':
            await self.app(scope, receive, send)
            return

        db = get_global_database()
        token = set_database_context(db)

        try:
            await self.app(scope, receive, send)
        finally:
            reset_database_context(token)

def create_middlewares(app: FastAPI):
    # 1. Database Context Middleware
    app.add_middleware(DatabaseContextMiddleware)
    
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:3000",
            "http://localhost:5173",
            "https://localhost:5173",
            "http://localhost:8000",  # 백엔드 자체
            "https://localhost:8000",  # 백엔드 HTTPS
            "https://chuchu-tree.duckdns.org",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],  # 응답 헤더 노출
    )
