from pydantic import Field

from app.config.base_config import BaseConfig


class ProdConfig(BaseConfig):
    """운영 환경 설정"""
    DEBUG: bool = Field(default=False, description="디버그 모드")

    # 백엔드 URL
    BACKEND_URL: str = Field(alias="PROD_BACKEND_URL", default="https://", description="백엔드 URL (비밀번호 재설정 링크 등에 사용)")

    # MySQL 포트
    MYSQL_HOST: str = Field(alias="PROD_MYSQL_HOST", default="localhost", description="MySQL 호스트")
    MYSQL_BINDING_PORT: int = Field(alias="PROD_MYSQL_BINDING_PORT", default=3308)
    MYSQL_PORT: int = Field(alias="PROD_MYSQL_PORT", default=3306)
    
    # Redis 포트
    REDIS_HOST: str = Field(alias="PROD_REDIS_HOST", default="localhost", description="Redis 호스트")
    REDIS_PORT: int = Field(alias="PROD_REDIS_PORT", default=6381)
    REDIS_BINDING_PORT: int = Field(alias="PROD_REDIS_BINDING_PORT", default=6381)
    
    # Storage 포트
    STORAGE_API_PORT: int = Field(alias="PROD_STORAGE_API_PORT", default=9004)
    STORAGE_CONSOLE_PORT: int = Field(alias="PROD_STORAGE_CONSOLE_PORT", default=9005)
    STORAGE_ENDPOINT: str = Field(alias="PROD_STORAGE_ENDPOINT", description="스토리지 엔드포인트", default="")
    
    # ================================
    # Storage 설정 (S3 호환)
    # ================================
    STORAGE_PROVIDER: str = Field(alias="LOCAL_STORAGE_PROVIDER", description="스토리지 제공자", default="")
    STORAGE_ACCESS_KEY: str = Field(alias="LOCAL_STORAGE_ACCESS_KEY", description="스토리지 액세스 키", default="")
    STORAGE_SECRET_KEY: str = Field(alias="LOCAL_STORAGE_SECRET_KEY", description="스토리지 시크릿 키", default="")
    STORAGE_BUCKET: str = Field(alias="LOCAL_STORAGE_BUCKET", description="스토리지 버킷명", default="")
    STORAGE_REGION: str = Field(alias="LOCAL_STORAGE_REGION", description="스토리지 리전", default="")
    STORAGE_PATH: str = Field(alias="PROD_STORAGE_PATH", description="로컬 스토리지 경로", default="")
    
    # ================================
    # OAuth Providers
    # ================================
    KAKAO_CLIENT_ID: str = Field(alias="KAKAO_CLIENT_ID", default="", description="카카오 클라이언트 아이디")
    KAKAO_CLIENT_SECRET: str = Field(alias="KAKAO_CLIENT_SECRET", default="", description="카카오 클라이언트 비밀키")
    KAKAO_REDIRECT_URI: str = Field(alias="PROD_KAKAO_REDIRECT_URI", default="http://localhost:8000/api/auth/kakao/callback", description="카카오 리다이렉트 URI")
    
    NAVER_CLIENT_ID: str = Field(alias="PROD_NAVER_CLIENT_ID", default="", description="네이버 클라이언트 아이디")
    NAVER_CLIENT_SECRET: str = Field(alias="PROD_NAVER_CLIENT_SECRET", default="", description="네이버 클라이언트 비밀키")
    NAVER_REDIRECT_URI: str = Field(alias="PROD_NAVER_REDIRECT_URI", default="http://localhost:8000/api/auth/naver/callback", description="네이버 리다이렉트 URI")

    FRONTEND_REDIRECT_URI: str = Field(alias="PROD_FRONTEND_REDIRECT_URI", default="https://chuchu-tree.duckdns.org", description="프론트엔드 리다이렉트 URI")