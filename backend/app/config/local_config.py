from pydantic import Field

from app.config.base_config import BaseConfig


class LocalConfig(BaseConfig):
    """로컬 환경 설정"""
    DEBUG: bool = Field(default=True, description="디버그 모드")

    # 백엔드 URL
    BACKEND_URL: str = Field(alias="LOCAL_BACKEND_URL", default="http://localhost:8000", description="백엔드 URL (비밀번호 재설정 링크 등에 사용)")

    # MySQL 포트
    MYSQL_HOST: str = Field(alias="LOCAL_MYSQL_HOST", default="localhost", description="MySQL 호스트")
    MYSQL_BINDING_PORT: int = Field(alias="LOCAL_MYSQL_BINDING_PORT", default=3306)
    MYSQL_PORT: int = Field(alias="LOCAL_MYSQL_PORT", default=3306)
    
    # Redis 포트
    REDIS_HOST: str = Field(alias="LOCAL_REDIS_HOST", default="localhost", description="Redis 호스트")
    REDIS_PORT: int = Field(alias="LOCAL_REDIS_PORT", default=6379)
    REDIS_BINDING_PORT: int = Field(alias="LOCAL_REDIS_BINDING_PORT", default=6379)
    
    # Storage 포트
    STORAGE_API_PORT: int = Field(alias="LOCAL_STORAGE_API_PORT", default=9000)
    STORAGE_CONSOLE_PORT: int = Field(alias="LOCAL_STORAGE_CONSOLE_PORT", default=9001)
    STORAGE_ENDPOINT: str = Field(alias="LOCAL_STORAGE_ENDPOINT", default="localhost", description="스토리지 엔드포인트")
    
    # ================================
    # Storage 설정 (S3 호환)
    # ================================
    STORAGE_PROVIDER: str = Field(alias="LOCAL_STORAGE_PROVIDER", default="minio", description="스토리지 제공자")
    STORAGE_ACCESS_KEY: str = Field(alias="LOCAL_STORAGE_ACCESS_KEY", default="minioadmin", description="스토리지 액세스 키")
    STORAGE_SECRET_KEY: str = Field(alias="LOCAL_STORAGE_SECRET_KEY", default="minioadmin", description="스토리지 시크릿 키")
    STORAGE_BUCKET: str = Field(alias="LOCAL_STORAGE_BUCKET", default="adkick-bucket", description="스토리지 버킷명")
    STORAGE_REGION: str = Field(alias="LOCAL_STORAGE_REGION", default="us-east-1", description="스토리지 리전")
    STORAGE_PATH: str = Field(alias="LOCAL_STORAGE_PATH", default="./storage_data", description="로컬 스토리지 경로")
    
    # ================================
    # OAuth Providers
    # ================================
    KAKAO_CLIENT_ID: str = Field(alias="KAKAO_CLIENT_ID", default="", description="카카오 클라이언트 아이디")
    KAKAO_CLIENT_SECRET: str = Field(alias="KAKAO_CLIENT_SECRET", default="", description="카카오 클라이언트 비밀키")
    KAKAO_REDIRECT_URI: str = Field(alias="LOCAL_KAKAO_REDIRECT_URI", default="http://localhost:8000/api/v1/auth/login/kakao/callback", description="카카오 리다이렉트 URI")
    
    NAVER_CLIENT_ID: str = Field(alias="DEV_NAVER_CLIENT_ID", default="", description="네이버 클라이언트 아이디")
    NAVER_CLIENT_SECRET: str = Field(alias="DEV_NAVER_CLIENT_SECRET", default="", description="네이버 클라이언트 비밀키")
    NAVER_REDIRECT_URI: str = Field(alias="LOCAL_NAVER_REDIRECT_URI", default="http://localhost:8000/api/v1/auth/login/naver/callback", description="네이버 리다이렉트 URI")

    GOOGLE_CLIENT_ID: str = Field(alias="GOOGLE_CLIENT_ID", default="", description="구글 클라이언트 아이디")
    GOOGLE_CLIENT_SECRET: str = Field(alias="GOOGLE_CLIENT_SECRET", default="", description="구글 클라이언트 비밀키")
    GOOGLE_REDIRECT_URI: str = Field(alias="LOCAL_GOOGLE_REDIRECT_URI", default="http://localhost:8000/api/v1/auth/login/google/callback", description="구글 리다이렉트 URI")

    GITHUB_CLIENT_ID: str = Field(alias="LOCAL_GITHUB_CLIENT_ID", default="", description="깃허브 클라이언트 아이디")
    GITHUB_CLIENT_SECRET: str = Field(alias="LOCAL_GITHUB_CLIENT_SECRET", default="", description="깃허브 클라이언트 비밀키")
    GITHUB_REDIRECT_URI: str = Field(alias="LOCAL_GITHUB_REDIRECT_URI", default="http://localhost:8000/api/v1/auth/login/github/callback", description="깃허브 리다이렉트 URI")

    FRONTEND_REDIRECT_URI: str = Field(alias="DEV_FRONTEND_REDIRECT_URI", default="https://chuchu-tree-dev.duckdns.org", description="프론트엔드 리다이렉트 URI")