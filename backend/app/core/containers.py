import os
from dependency_injector import containers, providers

from app.config.settings import get_settings
from app.core.database import Database

# ============================================================================
# Infrastructure - Clients
# ============================================================================
from app.common.infra.client.redis_client import AsyncRedisClient
from app.common.infra.client.storage_client import MinioClient, NCloudClient
from app.common.infra.client.kakao_oauth_client import KakaoOAuthClient
from app.common.infra.client.naver_oauth_client import NaverOAuthClient

# ============================================================================
# Infrastructure - Security
# ============================================================================
from app.common.infra.security.jwt_token_service import JwtTokenService
from app.common.infra.security.password_hasher import PasslibPasswordHasher
from app.common.infra.security.fastapi_cookie_service import FastAPICookieService

# ============================================================================
# Infrastructure - Gateways
# ============================================================================
from app.common.infra.gateway.storage_gateway_impl import StorageGatewayImpl
from app.common.infra.gateway.csrf_token_gateway_impl import CsrfTokenGatewayImpl

# ============================================================================
# Infrastructure - Events
# ============================================================================
from app.common.infra.event.in_memory_event_bus import get_event_bus

# ============================================================================
# Application Services
# ============================================================================
from app.common.application.service.auth_application_service import AuthApplicationService
from app.user.application.service.user_account_application_service import UserAccountApplicationService
from app.user.infra.repository.user_account_repository_impl import UserAccountRepositoryImpl

# ============================================================================
# Domain Repositories (Interfaces - Implementations to be added)
# ============================================================================
# from app.user.infra.repository.user_account_repository_impl import UserAccountRepositoryImpl
# from app.baekjoon.infra.repository.baekjoon_account_repository_impl import BaekjoonAccountRepositoryImpl
# from app.problem.infra.repository.problem_repository_impl import ProblemRepositoryImpl
# from app.tag.infra.repository.tag_repository_impl import TagRepositoryImpl
# from app.target.infra.repository.target_repository_impl import TargetRepositoryImpl
# from app.tier.infra.repository.tier_repository_impl import TierRepositoryImpl
# from app.activity.infra.repository.user_activity_repository_impl import UserActivityRepositoryImpl
# from app.recommendation.infra.repository.level_filter_repository_impl import LevelFilterRepositoryImpl
# from app.recommendation.infra.repository.tag_skill_repository_impl import TagSkillRepositoryImpl


class Container(containers.DeclarativeContainer):
    """
    중앙 의존성 주입 컨테이너

    - Singleton: 상태를 가지지 않거나, 애플리케이션 전체에서 하나만 존재해야 하는 객체
    - Factory: 매번 새로운 인스턴스가 필요한 객체
    - Configuration: 설정 값
    """

    wiring_config = containers.WiringConfiguration(
        packages=[
            "app.common.presentation",
            "app.user.presentation",
            "app.baekjoon.presentation",
            "app.problem.presentation",
            "app.tag.presentation",
            "app.target.presentation",
            "app.activity.presentation",
            "app.recommendation.presentation",
        ],
    )

    # ========================================================================
    # Configuration (환경 설정)
    # ========================================================================
    config = providers.Singleton(get_settings)

    # ========================================================================
    # Infrastructure - Database
    # ========================================================================
    db_url = providers.Callable(
        lambda settings: (
            f"mysql+aiomysql://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}"
            f"@{settings.MYSQL_HOST}:{settings.MYSQL_BINDING_PORT}/{settings.MYSQL_DATABASE}"
        ),
        settings=config
    )

    database = providers.Singleton(
        Database,
        db_url=db_url,
    )

    # ========================================================================
    # Infrastructure - Redis Client (Singleton)
    # ========================================================================
    redis_client = providers.Singleton(
        AsyncRedisClient,
        settings=config,
    )

    # ========================================================================
    # Infrastructure - Storage Client (Singleton, Factory Pattern)
    # ========================================================================
    storage_client = providers.Singleton(
        lambda settings: (
            MinioClient() if settings.STORAGE_PROVIDER == "minio"
            else NCloudClient()
        ),
        settings=config,
    )

    # ========================================================================
    # Infrastructure - Security Services (Singleton)
    # ========================================================================
    token_service = providers.Singleton(
        JwtTokenService,
        secret_key=providers.Callable(lambda s: s.SECRET_KEY, s=config),
        algorithm=providers.Callable(lambda s: s.JWT_ALGORITHM, s=config),
    )

    password_hasher = providers.Singleton(
        PasslibPasswordHasher,
    )

    cookie_service = providers.Singleton(
        FastAPICookieService,
        environment=providers.Callable(lambda: os.getenv("environment", "local")),
    )

    # ========================================================================
    # Infrastructure - Gateways (Singleton)
    # ========================================================================
    csrf_token_gateway = providers.Singleton(
        CsrfTokenGatewayImpl,
        redis_client=redis_client,
    )

    storage_gateway = providers.Singleton(
        StorageGatewayImpl,
        storage_client=storage_client,
    )

    # ========================================================================
    # Infrastructure - OAuth Clients
    # ========================================================================
    kakao_oauth_client = providers.Singleton(
        KakaoOAuthClient,
        csrf_gateway=csrf_token_gateway,
    )

    naver_oauth_client = providers.Singleton(
        NaverOAuthClient,
        csrf_gateway=csrf_token_gateway,
    )

    # ========================================================================
    # Infrastructure - Event Bus (전역 싱글톤)
    # ========================================================================
    domain_event_bus = providers.Singleton(
        get_event_bus,
    )

    # ========================================================================
    # Application Services
    # ========================================================================
    auth_application_service = providers.Singleton(
        AuthApplicationService,
        token_service=token_service,
        cookie_service=cookie_service,
        domain_event_bus=domain_event_bus,
        kakao_oauth_client=kakao_oauth_client,
        naver_oauth_client=naver_oauth_client
    )

    # ========================================================================
    # UserAccount (유저의 계정 도메인) 
    # ========================================================================

    # ========================================================================
    # Infrastructure
    # ========================================================================
    user_account_repository = providers.Singleton(
        UserAccountRepositoryImpl,
        db=database,
    )
    
    # ========================================================================
    # Application Services
    # ========================================================================
    
    user_account_application_service = providers.Singleton(
        UserAccountApplicationService,
        user_account_repository = user_account_repository
    )
    
    def init_resources(self):
        """앱 시작 시점에 싱글톤 객체들을 미리 생성"""
        # 1. 인프라 클라이언트 (Redis, Storage 등)
        self.redis_client()
        self.storage_client()
        
        # 2. 이벤트 핸들러가 등록되어야 하는 서비스들
        self.auth_application_service()
        self.user_account_application_service()
    
    #
    # baekjoon_account_repository = providers.Factory(
    #     BaekjoonAccountRepositoryImpl,
    #     db=database,
    # )
    #
    # problem_repository = providers.Factory(
    #     ProblemRepositoryImpl,
    #     db=database,
    # )
    #
    # tag_repository = providers.Factory(
    #     TagRepositoryImpl,
    #     db=database,
    # )
    #
    # target_repository = providers.Factory(
    #     TargetRepositoryImpl,
    #     db=database,
    # )
    #
    # tier_repository = providers.Factory(
    #     TierRepositoryImpl,
    #     db=database,
    # )
    #
    # user_activity_repository = providers.Factory(
    #     UserActivityRepositoryImpl,
    #     db=database,
    # )
    #
    # level_filter_repository = providers.Factory(
    #     LevelFilterRepositoryImpl,
    #     db=database,
    # )
    #
    # tag_skill_repository = providers.Factory(
    #     TagSkillRepositoryImpl,
    #     db=database,
    # )

    # ========================================================================
    # Use Cases / Application Services (구현되면 추가)
    # ========================================================================
    # user_registration_use_case = providers.Factory(
    #     UserRegistrationUseCase,
    #     user_repository=user_account_repository,
    #     password_hasher=password_hasher,
    #     event_bus=event_bus,
    # )
