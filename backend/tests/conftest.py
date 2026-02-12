import os
from datetime import datetime, timedelta

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from asgi_lifespan import LifespanManager

from app.common.domain.service.token_service import TokenService
from app.user.domain.entity.user_account import UserAccount
from app.common.domain.enums import Provider

# =============================================================================
# pytest 설정 훅 (가장 먼저 실행)
# =============================================================================

def pytest_configure():
    """pytest 시작 전 환경변수 설정 - Database 인스턴스 생성 전에 실행됨"""
    os.environ['TEST_MODE'] = 'true'
    os.environ['environment'] = 'local'


# =============================================================================
# 앱 & 클라이언트 Fixtures (통합 테스트의 기반)
# =============================================================================

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def app_with_container():
    """세션 스코프 - lifespan을 통해 Container 초기화된 앱 인스턴스"""
    from app.main import app
    async with LifespanManager(app) as manager:
        yield manager.app


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def client(app_with_container):
    """함수 스코프 - 매 테스트마다 새 AsyncClient 생성"""
    transport = ASGITransport(app=app_with_container)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def test_user(integration_session) -> UserAccount:
    """통합 테스트용 테스트 유저 - integration_session의 커넥션을 공유

    소셜 로그인 기반 앱이므로 API를 통한 유저 생성이 어려워
    DB에 직접 유저를 생성합니다.
    integration_session과 같은 커넥션을 사용하여 이벤트 루프 충돌을 방지합니다.
    """
    from app.user.infra.model.user_account import UserAccountModel

    session = integration_session

    now = datetime.now()
    model = UserAccountModel(
        provider=Provider.KAKAO,
        provider_id="test_provider_id_12345",
        email="test@example.com",
        profile_image=None,
        registered_at=now,
        created_at=now,
        updated_at=now,
    )
    session.add(model)
    await session.flush()

    yield UserAccount(
        user_account_id=model.user_account_id,
        provider=Provider.KAKAO,
        provider_id="test_provider_id_12345",
        email="test@example.com",
        profile_image=None,
        registered_at=now,
        created_at=now,
        updated_at=now,
    )


# =============================================================================
# DB_SESSION 환경변수 자동 설정 (unit/test 분기)
# =============================================================================

@pytest.fixture(scope="function", autouse=True)
def set_db_session_for_tests(request, monkeypatch):
    """테스트 경로에 따라 DB_SESSION 환경변수를 자동 설정.

    - tests/unit → DB_SESSION=unit (@transactional 완전 우회)
    - tests/integration → DB_SESSION=test (@transactional flush 모드)
    """
    test_path = str(request.fspath)
    if "tests/unit" in test_path or "tests\\unit" in test_path:
        monkeypatch.setenv('DB_SESSION', 'unit')
    elif "tests/integration" in test_path or "tests\\integration" in test_path:
        monkeypatch.setenv('DB_SESSION', 'test')


# =============================================================================
# 단위 테스트용 Mock Database Context
# =============================================================================

@pytest.fixture
def mock_database_context():
    """
    단위 테스트에서 @transactional 데코레이터가 적용된 메서드를 테스트할 때 사용.
    Mock Database를 ContextVar에 설정하여 get_database_instance() 호출이 성공하도록 함.
    Repository 테스트를 위해 _session_context도 함께 설정.
    """
    from contextlib import asynccontextmanager
    from unittest.mock import AsyncMock, MagicMock
    from app.core.database import _database_instance, _session_context

    # Mock Database 인스턴스 생성
    mock_db = MagicMock()
    mock_db._is_test_mode = True

    # Mock session (AsyncMock for async operations like execute)
    mock_session = AsyncMock()

    # execute() 결과를 적절히 Mock (scalars().first() → None, scalars().all() → [])
    mock_execute_result = MagicMock()
    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    mock_scalars.all.return_value = []
    mock_scalars.one_or_none.return_value = None
    mock_execute_result.scalars.return_value = mock_scalars
    mock_execute_result.scalar.return_value = None
    mock_execute_result.scalar_one.return_value = 0
    mock_execute_result.scalar_one_or_none.return_value = None
    mock_execute_result.fetchone.return_value = None
    mock_execute_result.fetchall.return_value = []
    mock_session.execute = AsyncMock(return_value=mock_execute_result)

    # begin_nested() → async context manager (SAVEPOINT mock)
    mock_nested = MagicMock()
    mock_nested.__aenter__ = AsyncMock(return_value=None)
    mock_nested.__aexit__ = AsyncMock(return_value=False)
    mock_session.begin_nested.return_value = mock_nested

    # Async context manager for test_session and session
    @asynccontextmanager
    async def mock_session_context():
        yield mock_session

    mock_db.session = mock_session_context
    mock_db.test_session = mock_session_context
    mock_db.get_current_session = MagicMock(return_value=mock_session)

    # ContextVar에 설정
    db_token = _database_instance.set(mock_db)
    session_token = _session_context.set(mock_session)

    yield mock_db

    # 정리
    _session_context.reset(session_token)
    _database_instance.reset(db_token)

# =============================================================================
# 통합테스트용 DB 세션 (Savepoint 패턴 - 테스트 후 롤백)
# =============================================================================

@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def integration_session(app_with_container):
    """통합테스트용 DB 세션 - 단일 커넥션으로 모든 작업 처리

    커넥션 레벨 트랜잭션 관리 (SQLAlchemy 공식 테스트 패턴):
    - engine.connect()로 풀과 독립된 전용 커넥션 확보
    - test_user와 API 요청이 같은 커넥션/세션을 공유하여 이벤트 루프 충돌 방지
    - DB_SESSION=test 모드에서 @transactional은 기존 세션이 있으면 flush만 수행
    - 테스트 종료 시 rollback으로 모든 데이터 정리
    """
    from contextlib import asynccontextmanager
    from sqlalchemy.ext.asyncio import AsyncSession
    from app.core.database import (
        get_global_database, _session_context
    )

    db = get_global_database()

    conn = await db._engine.connect()
    transaction = await conn.begin()
    session = AsyncSession(bind=conn, expire_on_commit=False)

    # _session_context에 세션 설정 → @transactional이 이 세션을 재사용
    token = _session_context.set(session)

    # db.session / db.test_session도 오버라이드 (fallback 경로 대비)
    original_session = db.session
    original_test_session = db.test_session

    @asynccontextmanager
    async def override_session():
        yield session

    db.session = override_session
    db.test_session = override_session

    yield session

    # 정리: 원래 메서드 복원, 롤백 → 모든 데이터 삭제
    _session_context.reset(token)
    db.session = original_session
    db.test_session = original_test_session
    await session.close()
    await transaction.rollback()
    await conn.close()


@pytest_asyncio.fixture(scope="function", loop_scope="session")
async def integration_client(app_with_container, integration_session):
    """통합테스트용 클라이언트 - integration_session의 커넥션을 공유"""
    transport = ASGITransport(app=app_with_container)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac



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
