from dependency_injector import containers, providers

from app.config.settings import get_settings
from app.core.database import Database, database_instance

settings = get_settings()

# DB URL을 전역적으로 설정
SQLALCHEMY_DATABASE_URL = (
    f"mysql+aiomysql://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}"
    f"@{settings.MYSQL_HOST}:{settings.MYSQL_BINDING_PORT}/{settings.MYSQL_DATABASE}"
)

class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=
        [
        ],
    )

    # Database
    db = providers.Singleton(
        Database,
        db_url=SQLALCHEMY_DATABASE_URL,
    )
    
    # 전역 인스턴스 생성
    database_instance = db