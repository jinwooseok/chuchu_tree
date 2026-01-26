
import os

from app.config.dev_config import DevConfig
from app.config.local_config import LocalConfig
from app.config.prod_config import ProdConfig


def get_settings():
    """환경에 따라 적절한 설정 클래스 반환"""
    env = os.getenv("environment", "local")
    
    if env == "dev":
        return DevConfig()
    elif env == "prod":
        return ProdConfig()
    else:
        return LocalConfig()

# 전역 설정 인스턴스
settings = get_settings()