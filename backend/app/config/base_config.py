from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent

class BaseConfig(BaseSettings):
    """기본 설정 클래스"""
    
    # ================================
    # 앱 기본 설정
    # ================================
    APP_NAME: str = Field(default="chuchu_tree", description="애플리케이션 이름")
    DEBUG: bool = Field(default=False, description="디버그 모드")
    VERSION: str = Field(default="0.0.1", description="애플리케이션 버전")
    SECRET_KEY: str = Field(default="change-me-in-production", description="JWT 암호화 키")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT 알고리즘")
    
    # ================================
    # MySQL 설정
    # ================================
    MYSQL_DATABASE: str = Field(default="chuchu_db", description="MySQL 데이터베이스명")
    MYSQL_USERNAME: str = Field(default="chuchu_user", description="MySQL 사용자명")
    MYSQL_PASSWORD: str = Field(default="", description="MySQL 비밀번호")
    MYSQL_ROOT_PASSWORD: str = Field(default="", description="MySQL 루트 비밀번호")
    MYSQL_VOLUME: str = Field(default="./mysql_data", description="MySQL 볼륨 경로")
    
    # ================================
    # Redis 설정  
    # ================================
    REDIS_PASSWORD: str = Field(default="1234", description="Redis 비밀번호")
    REDIS_DB: int = Field(default=0, description="Redis 데이터베이스 번호")
    REDIS_MAX_CONNECTIONS: int = Field(default=30, description="Redis 최대 연결 수")
    REDIS_SOCKET_TIMEOUT: int = Field(default=30, description="Redis 소켓 타임아웃 (초)")
    REDIS_CONNECT_TIMEOUT: int = Field(default=5, description="Redis 연결 타임아웃 (초)")
    REDIS_HEALTH_CHECK_INTERVAL: int = Field(default=30, description="Redis 헬스체크 간격 (초)")
    REDIS_DATA_PATH: str = Field(default="./redis_data", description="Redis 데이터 경로")

    # ================================
    # OAuth Providers
    # ================================
    KAKAO_CLIENT_ID: str = Field(default="", description="카카오 클라이언트 아이디")
    KAKAO_CLIENT_SECRET: str = Field(default="", description="카카오 클라이언트 비밀키")
    KAKAO_REDIRECT_URI: str = Field(default="http://localhost:8000/api/auth/kakao/callback", description="카카오 리다이렉트 URI")
    
    NAVER_CLIENT_ID: str = Field(default="", description="네이버 클라이언트 아이디")
    NAVER_CLIENT_SECRET: str = Field(default="", description="네이버 클라이언트 비밀키")
    NAVER_REDIRECT_URI: str = Field(default="http://localhost:8000/api/auth/naver/callback", description="네이버 리다이렉트 URI")

    FRONTEND_REDIRECT_URI: str = Field(default="https://adkick.co.kr", description="프론트엔드 리다이렉트 URI")

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        env_nested_delimiter="__",  # 중첩 환경 변수 지원
        case_sensitive=True,        # 대소문자 구분
        extra="ignore"              # 추가 필드 무시
    )
    