import os
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager
from datetime import timedelta

from app.common.domain.service.token_service import TokenService
from app.user.domain.entity.user_account import UserAccount

# =============================================================================
# pytest 설정 훅 (가장 먼저 실행)
# =============================================================================

def pytest_configure(config):
    """pytest 시작 전 환경변수 설정 - Database 인스턴스 생성 전에 실행됨"""
    os.environ['TEST_MODE'] = 'true'
    os.environ['environment'] = 'test'


# =============================================================================
# 앱 및 컨테이너 Fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app_with_container():
    """앱 + 컨테이너 초기화 (세션 범위)"""
    from app.main import app
    async with LifespanManager(app) as manager:
        yield manager.app


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def client(app_with_container):
    """테스트용 AsyncClient - 각 테스트마다 새로운 클라이언트"""
    from app.core.database import get_global_database, set_database_context, reset_database_context

    db = get_global_database()
    token = set_database_context(db)

    try:
        transport = ASGITransport(app=app_with_container)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac
    finally:
        reset_database_context(token)


# =============================================================================
# 테스트 유저 Fixtures (세션 범위)
# =============================================================================

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def test_user(app_with_container):
    """테스트용 유저 생성 (세션 범위) - 실제 서비스를 통해 생성"""
    from app.main import app
    from app.core.database import get_global_database, set_database_context, reset_database_context
    from app.user.application.command.user_account_command import CreateUserAccountCommand

    # app_with_container를 통해 lifespan이 실행되었음을 보장
    _ = app_with_container

    # database context 설정
    db = get_global_database()
    token = set_database_context(db)

    try:
        container = app.container
        user_service = container.user_account_application_service()

        command = CreateUserAccountCommand(
            provider="KAKAO",
            provider_id="test_provider_id_for_integration_test",
            email="test@example.com"
        )

        result = await user_service.create_or_find_user_account(command)

        yield result
    finally:
        reset_database_context(token)


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_user_id(test_user: "UserAccount") -> int:
    """테스트 유저 ID"""
    return test_user.user_account_id


# =============================================================================
# 인증 관련 Fixtures
# =============================================================================

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def token_service(app_with_container):
    """앱 컨테이너의 토큰 서비스 (환경변수 주입됨)"""
    from app.main import app
    _ = app_with_container  # lifespan 실행 보장
    return app.container.token_service()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def valid_access_token(token_service: "TokenService", test_user_id: int) -> str:
    """유효한 액세스 토큰"""
    return token_service.create_token(
        payload={"user_account_id": test_user_id},
        expires_delta=timedelta(hours=6)
    )


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def expired_access_token(token_service: "TokenService", test_user_id: int) -> str:
    """만료된 액세스 토큰"""
    return token_service.create_token(
        payload={"user_account_id": test_user_id},
        expires_delta=timedelta(seconds=-1)
    )


@pytest.fixture
def invalid_access_token() -> str:
    """유효하지 않은 토큰 형식"""
    return "invalid.token.format"


@pytest_asyncio.fixture(loop_scope="session")
async def authenticated_client(client: "AsyncClient", valid_access_token):
    """인증된 클라이언트 (쿠키에 토큰 설정)"""
    client.cookies.set("access_token", valid_access_token)
    return client
