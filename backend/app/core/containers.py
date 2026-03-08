import os
from dependency_injector import containers, providers

# ============================================================================
# Study domain imports
# ============================================================================
from app.study.infra.repository.study_repository_impl import StudyRepositoryImpl
from app.study.infra.repository.study_invitation_repository_impl import StudyInvitationRepositoryImpl
from app.study.infra.repository.study_application_repository_impl import StudyApplicationRepositoryImpl
from app.study.infra.repository.study_problem_repository_impl import StudyProblemRepositoryImpl
from app.study.infra.repository.notice_repository_impl import NoticeRepositoryImpl
from app.study.infra.repository.user_search_repository_impl import UserSearchRepositoryImpl
from app.study.infra.sse.notice_manager import NoticeSSEManager
from app.study.application.usecase.search_user_usecase import SearchUserUsecase
from app.study.application.usecase.create_study_usecase import CreateStudyUsecase
from app.study.application.usecase.get_study_detail_usecase import GetStudyDetailUsecase
from app.study.application.usecase.search_study_usecase import SearchStudyUsecase
from app.study.application.usecase.update_study_usecase import UpdateStudyUsecase
from app.study.application.usecase.delete_study_usecase import DeleteStudyUsecase
from app.study.application.usecase.get_my_studies_usecase import GetMyStudiesUsecase
from app.study.application.usecase.validate_study_name_usecase import ValidateStudyNameUsecase
from app.study.application.usecase.leave_study_usecase import LeaveStudyUsecase
from app.study.application.usecase.kick_study_member_usecase import KickStudyMemberUsecase
from app.study.application.usecase.send_study_invitation_usecase import SendStudyInvitationUsecase
from app.study.application.usecase.cancel_study_invitation_usecase import CancelStudyInvitationUsecase
from app.study.application.usecase.get_my_invitations_usecase import GetMyInvitationsUsecase
from app.study.application.usecase.get_my_pending_requests_usecase import GetMyPendingRequestsUsecase
from app.study.application.usecase.accept_study_invitation_usecase import AcceptStudyInvitationUsecase
from app.study.application.usecase.reject_study_invitation_usecase import RejectStudyInvitationUsecase
from app.study.application.usecase.apply_to_study_usecase import ApplyToStudyUsecase
from app.study.application.usecase.cancel_study_application_usecase import CancelStudyApplicationUsecase
from app.study.application.usecase.get_study_applications_usecase import GetStudyApplicationsUsecase
from app.study.application.usecase.accept_study_application_usecase import AcceptStudyApplicationUsecase
from app.study.application.usecase.reject_study_application_usecase import RejectStudyApplicationUsecase
from app.study.application.usecase.assign_study_problem_all_usecase import AssignStudyProblemAllUsecase
from app.study.application.usecase.assign_study_problem_usecase import AssignStudyProblemUsecase
from app.study.application.usecase.delete_study_problem_usecase import DeleteStudyProblemUsecase
from app.study.application.usecase.get_study_problems_usecase import GetStudyProblemsUsecase
from app.study.application.usecase.get_my_notices_usecase import GetMyNoticesUsecase
from app.study.application.usecase.mark_notices_read_usecase import MarkNoticesReadUsecase
from app.study.application.usecase.get_study_invitations_usecase import GetStudyInvitationsUsecase
from app.study.application.usecase.recommend_study_problems_usecase import RecommendStudyProblemsUsecase
from app.study.application.service.study_withdrawal_service import StudyWithdrawalService

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
from app.common.infra.client.storage_client import S3Client
from app.common.infra.repository.system_log_repository_impl import SystemLogRepositoryImpl
from app.baekjoon.infra.scheduler.metric_scheduler import BjAccountUpdateScheduler
from app.config.settings import get_settings
from app.core.database import Database, set_global_database
from app.middlewares import DatabaseContextMiddleware
from app.recommendation.application.usecase.recommend_problems_usecase import RecommendProblemsUsecase
from app.recommendation.application.usecase.get_recommendation_history_usecase import GetRecommendationHistoryUsecase
from app.recommendation.application.usecase.get_study_recommendation_history_usecase import GetStudyRecommendationHistoryUsecase
from app.recommendation.application.service.recommendation_history_service import RecommendationHistoryService
from app.recommendation.infra.repository.level_filter_repository_impl import LevelFilterRepositoryImpl
from app.recommendation.infra.repository.recommendation_history_repository_impl import RecommendationHistoryRepositoryImpl
from app.tag.application.service.tag_application_service import TagApplicationService
from app.target.application.service.target_application_service import TargetApplicationService
from app.tier.infra.repository.tier_repository_impl import TierRepositoryImpl

# ============================================================================
# Infrastructure - Clients
# ============================================================================
from app.common.infra.client.redis_client import AsyncRedisClient
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
from app.common.infra.gateway.storage_gateway_impl import S3StorageGatewayImpl
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
from app.user.application.usecase.get_tag_problems_usecase import GetTagProblemsUsecase
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
            "app.study.presentation",
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
    storage_client = providers.Singleton(S3Client)

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
        S3StorageGatewayImpl,
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
        domain_event_bus=domain_event_bus,
        storage_gateway=storage_gateway,
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
    # Study domain - Repositories (BJ usecase에서 사용하므로 먼저 선언)
    # ========================================================================
    study_repository = providers.Singleton(StudyRepositoryImpl, db=database)
    study_invitation_repository = providers.Singleton(StudyInvitationRepositoryImpl, db=database)
    study_application_repository = providers.Singleton(StudyApplicationRepositoryImpl, db=database)
    study_problem_repository = providers.Singleton(StudyProblemRepositoryImpl, db=database)
    notice_repository = providers.Singleton(NoticeRepositoryImpl, db=database)
    user_search_repository = providers.Singleton(UserSearchRepositoryImpl, db=database)

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
        problem_update_service=problem_update_service,
    )

    get_baekjoon_me_usecase = providers.Singleton(
        GetBaekjoonMeUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        user_date_record_repository=user_date_record_repository,
        tier_repository=tier_repository,
        domain_event_bus=domain_event_bus,
        study_repository=study_repository,
        user_search_repository=user_search_repository,
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

    recommendation_history_repository = providers.Singleton(
        RecommendationHistoryRepositoryImpl,
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

    # ========================================================================
    # Tag Problems Usecase
    # ========================================================================
    get_tag_problems_usecase = providers.Singleton(
        GetTagProblemsUsecase,
        baekjoon_account_repository=baekjoon_account_repository,
        tag_repository=tag_repository,
        problem_repository=problem_repository,
        user_activity_repository=user_activity_repository,
        tier_repository=tier_repository,
        target_repository=target_repository,
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
        target_repository=target_repository,
        domain_event_bus=domain_event_bus,
    )

    recommendation_history_service = providers.Singleton(
        RecommendationHistoryService,
        recommendation_history_repository=recommendation_history_repository,
    )

    get_recommendation_history_usecase = providers.Singleton(
        GetRecommendationHistoryUsecase,
        recommendation_history_repository=recommendation_history_repository,
    )

    get_study_recommendation_history_usecase = providers.Singleton(
        GetStudyRecommendationHistoryUsecase,
        recommendation_history_repository=recommendation_history_repository,
        study_repository=study_repository,
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

    # ========================================================================
    # Study domain - SSE Manager
    # ========================================================================
    notice_sse_manager = providers.Singleton(NoticeSSEManager)

    # ========================================================================
    # Study domain - Usecases
    # ========================================================================
    search_user_usecase = providers.Singleton(
        SearchUserUsecase,
        user_search_repository=user_search_repository,
        storage_gateway=storage_gateway,
    )

    validate_study_name_usecase = providers.Singleton(
        ValidateStudyNameUsecase,
        study_repository=study_repository,
    )

    create_study_usecase = providers.Singleton(
        CreateStudyUsecase,
        study_repository=study_repository,
        invitation_repository=study_invitation_repository,
        user_search_repository=user_search_repository,
    )

    get_study_detail_usecase = providers.Singleton(
        GetStudyDetailUsecase,
        study_repository=study_repository,
        user_search_repository=user_search_repository,
        invitation_repository=study_invitation_repository,
        application_repository=study_application_repository,
        storage_gateway=storage_gateway,
    )

    search_study_usecase = providers.Singleton(
        SearchStudyUsecase,
        study_repository=study_repository,
        storage_gateway=storage_gateway,
    )

    update_study_usecase = providers.Singleton(
        UpdateStudyUsecase,
        study_repository=study_repository,
    )

    delete_study_usecase = providers.Singleton(
        DeleteStudyUsecase,
        study_repository=study_repository,
    )

    get_my_studies_usecase = providers.Singleton(
        GetMyStudiesUsecase,
        study_repository=study_repository,
        user_search_repository=user_search_repository,
        storage_gateway=storage_gateway,
    )

    leave_study_usecase = providers.Singleton(
        LeaveStudyUsecase,
        study_repository=study_repository,
    )

    kick_study_member_usecase = providers.Singleton(
        KickStudyMemberUsecase,
        study_repository=study_repository,
    )

    send_study_invitation_usecase = providers.Singleton(
        SendStudyInvitationUsecase,
        study_repository=study_repository,
        invitation_repository=study_invitation_repository,
        user_search_repository=user_search_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    cancel_study_invitation_usecase = providers.Singleton(
        CancelStudyInvitationUsecase,
        study_repository=study_repository,
        invitation_repository=study_invitation_repository,
    )

    get_my_invitations_usecase = providers.Singleton(
        GetMyInvitationsUsecase,
        invitation_repository=study_invitation_repository,
        study_repository=study_repository,
        user_search_repository=user_search_repository,
        storage_gateway=storage_gateway,
    )

    get_my_pending_requests_usecase = providers.Singleton(
        GetMyPendingRequestsUsecase,
        invitation_repository=study_invitation_repository,
        application_repository=study_application_repository,
        study_repository=study_repository,
        user_search_repository=user_search_repository,
        storage_gateway=storage_gateway,
    )

    accept_study_invitation_usecase = providers.Singleton(
        AcceptStudyInvitationUsecase,
        invitation_repository=study_invitation_repository,
        study_repository=study_repository,
        application_repository=study_application_repository,
        user_search_repository=user_search_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    reject_study_invitation_usecase = providers.Singleton(
        RejectStudyInvitationUsecase,
        invitation_repository=study_invitation_repository,
        study_repository=study_repository,
        user_search_repository=user_search_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    apply_to_study_usecase = providers.Singleton(
        ApplyToStudyUsecase,
        study_repository=study_repository,
        application_repository=study_application_repository,
        user_search_repository=user_search_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    cancel_study_application_usecase = providers.Singleton(
        CancelStudyApplicationUsecase,
        study_repository=study_repository,
        application_repository=study_application_repository,
    )

    get_study_applications_usecase = providers.Singleton(
        GetStudyApplicationsUsecase,
        study_repository=study_repository,
        application_repository=study_application_repository,
        user_search_repository=user_search_repository,
        storage_gateway=storage_gateway,
    )

    accept_study_application_usecase = providers.Singleton(
        AcceptStudyApplicationUsecase,
        study_repository=study_repository,
        application_repository=study_application_repository,
        invitation_repository=study_invitation_repository,
        user_search_repository=user_search_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    reject_study_application_usecase = providers.Singleton(
        RejectStudyApplicationUsecase,
        study_repository=study_repository,
        application_repository=study_application_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    assign_study_problem_all_usecase = providers.Singleton(
        AssignStudyProblemAllUsecase,
        study_repository=study_repository,
        study_problem_repository=study_problem_repository,
        user_search_repository=user_search_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    assign_study_problem_usecase = providers.Singleton(
        AssignStudyProblemUsecase,
        study_repository=study_repository,
        study_problem_repository=study_problem_repository,
        user_search_repository=user_search_repository,
        notice_repository=notice_repository,
        notice_sse_manager=notice_sse_manager,
    )

    delete_study_problem_usecase = providers.Singleton(
        DeleteStudyProblemUsecase,
        study_repository=study_repository,
        study_problem_repository=study_problem_repository,
    )

    get_study_problems_usecase = providers.Singleton(
        GetStudyProblemsUsecase,
        study_repository=study_repository,
        study_problem_repository=study_problem_repository,
        user_search_repository=user_search_repository,
        domain_event_bus=domain_event_bus,
        problem_history_repository=problem_history_repository,
    )

    get_my_notices_usecase = providers.Singleton(
        GetMyNoticesUsecase,
        notice_repository=notice_repository,
        user_search_repository=user_search_repository,
        storage_gateway=storage_gateway,
    )

    mark_notices_read_usecase = providers.Singleton(
        MarkNoticesReadUsecase,
        notice_repository=notice_repository,
    )

    get_study_invitations_usecase = providers.Singleton(
        GetStudyInvitationsUsecase,
        study_repository=study_repository,
        invitation_repository=study_invitation_repository,
        user_search_repository=user_search_repository,
        storage_gateway=storage_gateway,
    )

    recommend_study_problems_usecase = providers.Singleton(
        RecommendStudyProblemsUsecase,
        study_repository=study_repository,
        user_search_repository=user_search_repository,
        problem_history_repository=problem_history_repository,
        recommend_problems_usecase=recommand_problems_usecase,
    )

    study_withdrawal_service = providers.Singleton(
        StudyWithdrawalService,
        study_repository=study_repository,
        study_problem_repository=study_problem_repository,
        notice_repository=notice_repository,
        study_invitation_repository=study_invitation_repository,
        study_application_repository=study_application_repository,
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
        self.study_withdrawal_service()
        self.recommendation_history_service()

        # 3. 스케줄러 시작 (추가)
        scheduler = self.bj_account_update_scheduler()
        scheduler.start()
        return self

    init_resources_provider = providers.Callable(init_resources)
