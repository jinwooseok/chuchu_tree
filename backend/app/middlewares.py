from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.core.database import get_global_database, reset_database_context, set_database_context

class DatabaseContextMiddleware(BaseHTTPMiddleware):
    """요청별로 Database 인스턴스를 ContextVar에 설정"""
    
    async def dispatch(self, request: Request, call_next):
        # 전역 Database 사용
        db = get_global_database()
        token = set_database_context(db)
        
        try:
            response = await call_next(request)
            return response
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
