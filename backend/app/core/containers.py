import os
from dependency_injector import containers, providers

from app.activity.infra.repository.user_date_record_repository_impl import UserDateRecordRepositoryImpl
from app.baekjoon.application.usecase.get_scheduler_inactive_periods_usecase import GetSchedulerInactivePeriodsUsecase
from app.baekjoon.application.usecase.get_unrecorded_problems_usecase import GetUnrecordedProblemsUsecase
from app.baekjoon.application.usecase.link_bj_account_usecase import LinkBjAccountUsecase
from app.baekjoon.application.usecase.get_baekjoon_me_usecase import GetBaekjoonMeUsecase
from app.baekjoon.application.usecase.get_monthly_problems_usecase import GetMonthlyProblemsUsecase
from app.baekjoon.application.usecase.get_streaks_usecase import GetStreaksUsecase
from app.baekjoon.application.usecase.update_bj_account_usecase import UpdateBjAccountUsecase
from app.baekjoon.infra.repository.baekjoon_account_repository_impl import BaekjoonAccountRepositoryImpl
from app.baekjoon.infra.repository.problem_history_repository_impl import ProblemHistoryRepositoryImpl
from app.common.infra.repository.system_log_repository_impl import SystemLogRepositoryImpl
from app.baekjoon.infra.scheduler.metric_scheduler import BjAccountUpdateScheduler
from app.config.settings import get_settings
from app.core.database import Database, set_global_database
from app.middlewares import DatabaseContextMiddleware
from app.recommendation.application.usecase.recommend_problems_usecase import RecommendProblemsUsecase
from app.recommendation.infra.repository.level_filter_repository_impl import LevelFilterRepositoryImpl
from app.tag.application.service.tag_application_service import TagApplicationService
from app.target.application.service.target_application_service import TargetApplicationService
from app.tier.infra.repository.tier_repository_impl import TierRepositoryImpl

# ============================================================================
# Infrastructure - Clients
# ============================================================================
from app.common.infra.client.redis_client import AsyncRedisClient
from app.common.infra.client.storage_client import MinioClient, NCloudClient
from app.common.infra.client.kakao_oauth_client import KakaoOAuthClient
from app.common.infra.client.naver_oauth_client import NaverOAuthClient
from app.common.infra.client.google_oauth_client import GoogleOAuthClient
from app.common.infra.client.github_oauth_client import GitHubOAuthClient

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
from app.common.infra.gateway.refresh_token_whitelist_gateway_impl import RefreshTokenWhitelistGatewayImpl
from app.baekjoon.infra.gateway.solvedac_gateway_impl import SolvedacGatewayImpl

# ============================================================================
# Infrastructure - Events
# ============================================================================
from app.common.infra.event.in_memory_event_bus import get_event_bus

# ============================================================================
# Application Services
# ============================================================================
from app.activity.application.service.activity_application_service import ActivityApplicationService
from app.common.application.service.auth_application_service import AuthApplicationService
from app.problem.application.service.problem_application_service import ProblemApplicationService
from app.problem.application.service.problem_metadata_sync_service import ProblemMetadataSyncService
from app.problem.application.service.problem_update_service import ProblemUpdateService
from app.user.application.service.user_account_application_service import UserAccountApplicationService
from app.user.infra.repository.user_account_repository_impl import UserAccountRepositoryImpl

# ============================================================================
# Domain Repositories
# ============================================================================
from app.activity.infra.repository.user_activity_repository_impl import UserActivityRepositoryImpl
from app.problem.infra.repository.problem_repository_impl import ProblemRepositoryImpl
from app.recommendation.infra.repository.tag_skill_repository_impl import TagSkillRepositoryImpl
from app.tag.infra.repository.tag_repository_impl import TagRepositoryImpl
from app.target.infra.repository.target_repository_impl import TargetRepositoryImpl
from app.user.application.usecase.get_user_tags_usecase import GetUserTagsUsecase


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

    database_middleware = providers.Factory(
        DatabaseContextMiddleware,
        db=database,
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

    refresh_token_whitelist_gateway = providers.Singleton(
        RefreshTokenWhitelistGatewayImpl,
        redis_client=redis_client,
    )

    storage_gateway = providers.Singleton(
        StorageGatewayImpl,
        storage_client=storage_client,
    )

    solvedac_gateway = providers.Singleton(
        SolvedacGatewayImpl,
        request_delay=0.3,
        concurrent_requests=5,  # 동시에 5개 페이지씩 요청
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

    google_oauth_client = providers.Singleton(
        GoogleOAuthClient,
        csrf_gateway=csrf_token_gateway,
    )

    github_oauth_client = providers.Singleton(
        GitHubOAuthClient,
        csrf_gateway=csrf_token_gateway,
    )

    # ========================================================================
    # Infrastructure - Event Bus (전역 싱글톤)
    # ========================================================================
    domain_event_bus = providers.Singleton(
        get_event_bus,
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
        user_account_repository=user_account_repository,
        domain_event_bus=domain_event_bus
    )

    # ========================================================================
    # Tier (티어 도메인)
    # ========================================================================
    tier_repository = providers.Singleton(
        TierRepositoryImpl,
        db=database,
    )

    # ========================================================================
    # BaekjoonAccount (백준 계정 도메인)
    # ========================================================================

    # ========================================================================
    # Infrastructure
    # ========================================================================
    baekjoon_account_repository = providers.Singleton(
        BaekjoonAccountRepositoryImpl,
        db=database,
    )

    problem_history_repository = providers.Singleton(
        ProblemHistoryRepositoryImpl,
        db=database,
    )

    # ========================================================================
    # Activity domain - Repositories
    # ========================================================================
    user_activity_repository = providers.Singleton(
        UserActivityRepositoryImpl,
        db=database
    )

    user_date_record_repository = providers.Singleton(
        UserDateRecordRepositoryImpl,
        db=database
    )

    system_log_repository = providers.Singleton(
        SystemLogRepositoryImpl,
        db=database
    )

    # ========================================================================
    # Problem domain - Services (usecases below depend on these)
    # ========================================================================
    problem_update_service = providers.Singleton(
        ProblemUpdateService,
        db=database,
    )

    problem_metadata_sync_service = providers.Singleton(
        ProblemMetadataSyncService,
        db=database,
        system_log_repository=system_log_repository,
    )

    # ========================================================================
    # Application Services / Usecases
    # ========================================================================

    link_bj_account_usecase = providers.Singleton(
        LinkBjAccountUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        solvedac_gateway=solvedac_gateway,
        domain_event_bus=domain_event_bus,
        user_date_record_repository=user_date_record_repository,
        user_activity_repository=user_activity_repository,
    )

    get_baekjoon_me_usecase = providers.Singleton(
        GetBaekjoonMeUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        user_date_record_repository=user_date_record_repository,
        tier_repository=tier_repository,
        domain_event_bus=domain_event_bus
    )

    get_streaks_usecase = providers.Singleton(
        GetStreaksUsecase,
        user_date_record_repository=user_date_record_repository,
        baekjoon_account_repository=baekjoon_account_repository
    )

    update_bj_account_usecase = providers.Singleton(
        UpdateBjAccountUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        problem_history_repository=problem_history_repository,
        solvedac_gateway=solvedac_gateway,
        user_date_record_repository=user_date_record_repository,
        user_activity_repository=user_activity_repository,
        system_log_repository=system_log_repository,
        problem_update_service=problem_update_service,
    )

    get_unrecorded_problems_usecase = providers.Singleton(
        GetUnrecordedProblemsUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        problem_history_repository=problem_history_repository,
        domain_event_bus=domain_event_bus
    )

    get_scheduler_inactive_periods_usecase = providers.Singleton(
        GetSchedulerInactivePeriodsUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        system_log_repository=system_log_repository,
    )

    # ========================================================================
    # Activity domain - Application Service
    # ========================================================================
    activity_application_service = providers.Singleton(
        ActivityApplicationService,
        user_activity_repository=user_activity_repository,
        domain_event_bus=domain_event_bus,
        baekjoon_account_repository=baekjoon_account_repository,
        problem_history_repository=problem_history_repository,
        user_date_record_repository=user_date_record_repository,
        problem_update_service=problem_update_service,
        system_log_repository=system_log_repository,
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
        naver_oauth_client=naver_oauth_client,
        google_oauth_client=google_oauth_client,
        github_oauth_client=github_oauth_client,
        refresh_token_whitelist=refresh_token_whitelist_gateway
    )

    # ========================================================================
    # Tag domain
    # ========================================================================
    tag_repository = providers.Singleton(
        TagRepositoryImpl,
        db=database
    )

    tag_application_service = providers.Singleton(
        TagApplicationService,
        tag_repository=tag_repository
    )

    # ========================================================================
    # Recommendation domain
    # ========================================================================
    tag_skill_repository = providers.Singleton(
        TagSkillRepositoryImpl,
        db=database
    )

    recommand_filter_repository = providers.Singleton(
        LevelFilterRepositoryImpl,
        db=database
    )

    # ========================================================================
    # Target domain
    # ========================================================================
    target_repository = providers.Singleton(
        TargetRepositoryImpl,
        db=database
    )

    target_application_service = providers.Singleton(
        TargetApplicationService,
        target_repository=target_repository
    )

    # ========================================================================
    # Problem domain
    # ========================================================================
    problem_repository = providers.Singleton(
        ProblemRepositoryImpl,
        db=database,
        system_log_repository=system_log_repository,
    )

    problem_application_service = providers.Singleton(
        ProblemApplicationService,
        problem_repository=problem_repository,
        tag_repository=tag_repository,
        target_repository=target_repository,
        tier_repository=tier_repository
    )

    # ========================================================================
    # Monthly Problems Usecase
    # ========================================================================
    get_monthly_problems_usecase = providers.Singleton(
        GetMonthlyProblemsUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        problem_history_repository=problem_history_repository,
        domain_event_bus=domain_event_bus
    )

    # ========================================================================
    # User Tags Usecase
    # ========================================================================
    get_user_tags_usecase = providers.Singleton(
        GetUserTagsUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        tag_repository=tag_repository,
        tag_skill_repository=tag_skill_repository,
        tier_repository=tier_repository,
        activity_repository=user_activity_repository
    )

    recommand_problems_usecase = providers.Singleton(
        RecommendProblemsUsecase,
        user_account_repository=user_account_repository,
        baekjoon_account_repository=baekjoon_account_repository,
        user_activity_repository=user_activity_repository,
        tag_repository=tag_repository,
        tag_skill_repository=tag_skill_repository,
        recommend_filter_repository=recommand_filter_repository,
        problem_repository=problem_repository,
        tier_repository=tier_repository,
        problem_history_repository=problem_history_repository,
        target_repository=target_repository
    )

    # ========================================================================
    # Scheduler (스케줄러)
    # ========================================================================
    bj_account_update_scheduler = providers.Singleton(
        BjAccountUpdateScheduler,
        update_bj_account_use_case=update_bj_account_usecase,
        problem_metadata_sync_service=problem_metadata_sync_service,
        system_log_repository=system_log_repository,
    )

    async def init_resources(self):
        """앱 시작 시점에 싱글톤 객체들을 미리 생성"""
        # 1. 인프라 클라이언트 (Redis, Storage 등)
        self.storage_client()
        db = self.database()
        set_global_database(db)
        redis = self.redis_client()
        await redis._initialize_client()
        # 2. 이벤트 핸들러가 등록되어야 하는 서비스들
        self.auth_application_service()
        self.user_account_application_service()
        self.link_bj_account_usecase()
        self.activity_application_service()
        self.problem_application_service()
        self.tag_application_service()
        self.target_application_service()

        # 3. 스케줄러 시작 (추가)
        scheduler = self.bj_account_update_scheduler()
        scheduler.start()
        return self

    init_resources_provider = providers.Callable(init_resources)
