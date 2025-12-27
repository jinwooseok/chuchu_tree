from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def create_middlewares(app: FastAPI):
    # CORS 설정
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost:5173",
            "https://localhost:5173",
            "http://localhost:8080",  # 백엔드 자체
            "https://localhost:8080",  # 백엔드 HTTPS
            "https://chuchu-tree.duckdns.org",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],  # 응답 헤더 노출
    )
