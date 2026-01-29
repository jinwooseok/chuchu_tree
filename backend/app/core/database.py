# app/core/db/database.py
from contextlib import asynccontextmanager
import functools
import logging
import os
from typing import Any, Awaitable, Callable, AsyncGenerator, Literal
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextvars import ContextVar

from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)

Base = declarative_base()

# ContextVar: 요청별로 격리된 저장소
_session_context: ContextVar[AsyncSession | None] = ContextVar('session', default=None)
_database_instance: ContextVar['Database | None'] = ContextVar('database', default=None)
_transaction_depth: ContextVar[int] = ContextVar('transaction_depth', default=0)

# ⭐ 전역 Database 인스턴스
_global_database: 'Database | None' = None


class Database:
    """
    데이터베이스 연결 및 세션 관리
    
    주요 기능:
    1. 연결 풀 관리 (create_async_engine)
    2. 세션 팩토리 (async_sessionmaker)
    3. 트랜잭션 세션 제공 (session, test_session)
    """
    
    def __init__(self, db_url: str, echo: bool = False) -> None:
        self._engine = create_async_engine(
            db_url,
            pool_pre_ping=True,         # 연결 유효성 검사
            pool_recycle=3600,          # 1시간마다 연결 재생성
            pool_size=10,               # 기본 연결 풀 크기
            max_overflow=20,            # 추가 연결 최대 개수
            pool_timeout=30,            # 연결 대기 시간 (초)
            echo=echo,                  # SQL 로깅
            future=True,                # SQLAlchemy 2.0 스타일
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autocommit=False,           # 명시적 commit 필요
            autoflush=False,            # 명시적 flush 필요
            expire_on_commit=False,     # commit 후에도 객체 사용 가능
        )
        self._is_test_mode = os.getenv('TEST_MODE', 'false') == 'true'

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        트랜잭션 세션 생성 (운영 환경)
        
        - 정상 완료: 자동 commit
        - 예외 발생: 자동 rollback
        - 항상: session.close()
        """
        session: AsyncSession = self._session_factory()
        token = _session_context.set(session)
        
        try:
            # 트랜잭션 시작
            async with session.begin():
                logger.debug("Transaction started")
                yield session
                # 정상 완료 시 자동 commit
                logger.debug("Transaction committed")
        except Exception as ex:
            # 예외 발생 시 자동 rollback (begin()의 __aexit__에서 처리)
            logger.error(f"Transaction rolled back due to: {ex}")
            raise
        finally:
            # 세션 정리
            _session_context.reset(token)
            await session.close()
            logger.debug("Session closed")

    @asynccontextmanager
    async def test_session(self) -> AsyncGenerator[AsyncSession, None]:
        """
        테스트용 세션 (모든 변경사항 롤백)
        
        - 테스트 완료 후 무조건 rollback
        - 테스트 간 데이터 격리 보장
        """
        session: AsyncSession = self._session_factory()
        token = _session_context.set(session)
        
        try:
            # 트랜잭션 시작
            transaction = await session.begin()
            logger.debug("Test transaction started")
            
            yield session
            
            # 테스트 완료 후 무조건 rollback
            await transaction.rollback()
            logger.debug("Test transaction rolled back")
            
        except Exception as ex:
            # 예외 발생 시에도 rollback
            logger.error(f"Test transaction error: {ex}")
            await transaction.rollback()
            raise
        finally:
            # 세션 정리
            _session_context.reset(token)
            await session.close()
            logger.debug("Test session closed")
    
    def get_current_session(self) -> AsyncSession:
        """
        현재 컨텍스트의 활성 세션 반환
        
        Raises:
            APIException: 활성 세션이 없는 경우
        """
        session = _session_context.get()
        if session is None:
            logger.error("No active session in context")
            raise APIException(ErrorCode.DATABASE_ERROR, "No active database session")
        return session

    async def close(self) -> None:
        """데이터베이스 엔진 종료"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")


# =============================================================================
# 전역 Database 관리 (Middleware용)
# =============================================================================

def set_global_database(db: Database) -> None:
    """
    앱 시작 시 전역 Database 설정
    Container의 init_resources()에서 호출
    """
    global _global_database
    _global_database = db
    logger.info("Global database instance set")


def get_global_database() -> Database:
    """
    전역 Database 반환
    Middleware에서 사용
    """
    if _global_database is None:
        logger.error("Global database not initialized")
        raise APIException(ErrorCode.DATABASE_ERROR, "Global database not initialized")
    return _global_database


# =============================================================================
# ContextVar 관리 함수 (요청별 격리)
# =============================================================================

def set_database_context(db: Database) -> Any:
    """
    요청 시작 시 Database 인스턴스를 ContextVar에 설정
    
    Returns:
        token: reset 시 사용할 토큰
    """
    return _database_instance.set(db)


def reset_database_context(token: Any) -> None:
    """
    요청 종료 시 ContextVar 정리
    """
    _database_instance.reset(token)


def get_database_instance() -> Database:
    """
    현재 컨텍스트의 Database 인스턴스 반환
    @transactional 데코레이터에서 사용
    
    Raises:
        APIException: Database 인스턴스가 설정되지 않은 경우
    """
    db = _database_instance.get()
    if db is None:
        logger.error("No database instance in context")
        raise APIException(ErrorCode.DATABASE_ERROR, "Database not initialized")
    return db


# =============================================================================
# 트랜잭션 데코레이터
# =============================================================================

def transactional(
    isolation_level: Literal["READ UNCOMMITTED", "READ COMMITTED", "REPEATABLE READ", "SERIALIZABLE"] | None = None,
    readonly: bool = False
):
    """
    트랜잭션 데코레이터
    
    특징:
    1. 중첩 트랜잭션 지원 (같은 세션 재사용)
    2. 테스트 모드 자동 감지
    3. 격리 레벨 설정 가능
    4. readonly 모드 지원
    
    Args:
        isolation_level: 트랜잭션 격리 레벨
        readonly: 읽기 전용 모드 (최적화)
    
    Usage:
        @transactional()
        async def create_user(user_data: dict):
            ...
        
        @transactional(isolation_level="SERIALIZABLE")
        async def transfer_points(from_id: int, to_id: int, points: int):
            ...
        
        @transactional(readonly=True)
        async def get_user_stats(user_id: int):
            ...
    """
    def decorator(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
        @functools.wraps(func)
        async def _wrapper(*args, **kwargs) -> Any:
            db = get_database_instance()
            
            # 현재 트랜잭션 깊이 확인
            depth = _transaction_depth.get()
            
            # 이미 세션이 있는지 확인 (중첩 트랜잭션)
            existing_session = _session_context.get()
            
            if existing_session is not None:
                # 중첩 트랜잭션: 기존 세션 재사용
                logger.debug(f"Reusing existing session (depth: {depth})")
                _transaction_depth.set(depth + 1)
                
                try:
                    result = await func(*args, **kwargs)
                    return result
                finally:
                    _transaction_depth.set(depth)
            
            else:
                # 새 트랜잭션 시작
                logger.debug(f"Starting new transaction (isolation: {isolation_level}, readonly: {readonly})")
                _transaction_depth.set(depth + 1)
                
                # 테스트 모드면 test_session, 아니면 일반 session
                session_context = db.test_session() if db._is_test_mode else db.session()
                
                try:
                    async with session_context as session:
                        # 격리 레벨 설정
                        if isolation_level:
                            await session.execute(text(f"SET TRANSACTION ISOLATION LEVEL {isolation_level}"))
                        
                        # readonly 최적화
                        if readonly:
                            await session.execute(text("SET TRANSACTION READ ONLY"))
                        
                        result = await func(*args, **kwargs)
                        return result
                        
                except APIException:
                    # 비즈니스 로직 예외는 그대로 전파
                    logger.warning(f"Business logic exception in transaction")
                    raise
                    
                except Exception as ex:
                    # 예상치 못한 예외는 DATABASE_ERROR로 래핑
                    logger.exception(f"Unexpected error in transaction: {ex}")
                    raise APIException(
                        ErrorCode.DATABASE_ERROR,
                        f"Database transaction failed: {str(ex)}"
                    )
                    
                finally:
                    _transaction_depth.set(depth)
        
        return _wrapper
    
    # 파라미터 없이 @transactional 사용 시 대응
    if callable(isolation_level):
        func = isolation_level
        isolation_level = None
        return decorator(func)
    
    return decorator


# 호환성을 위한 별칭
async_transactional = transactional