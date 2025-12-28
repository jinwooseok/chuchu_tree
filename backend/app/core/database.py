from contextlib import asynccontextmanager
import functools
import logging
import os
from typing import Any, Awaitable, Callable, AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextvars import ContextVar

from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger()

Base = declarative_base()

_session_context: ContextVar[AsyncSession] = ContextVar('session')

class Database:
    def __init__(self, db_url: str) -> None:
        self._engine = create_async_engine(
            db_url,
            pool_pre_ping=True,         # 연결 전 핑 테스트 (중요!)
            pool_recycle=7200,          # 2시간마다 재생성 (MySQL 8시간 타임아웃 대비)
            pool_size=10,               # 연결 풀 크기
            max_overflow=20,            # 최대 추가 연결
            pool_timeout=30,            # 연결 대기 시간
            pool_reset_on_return='commit',  # 반환 시 상태 리셋
            connect_args={
                "connect_timeout": 30,   # 연결 시간 초과
                "charset": "utf8mb4",
                "autocommit": False,
            },
            echo=False,                 # SQL 로깅 비활성화 (성능)
            future=True,               # SQLAlchemy 2.0 스타일
        )
        self._session_factory = async_sessionmaker(
            bind=self._engine,
            class_=AsyncSession,
            autocommit=False,
            autoflush=True if os.getenv('DB_SESSION', 'local').lower() == 'test' else False,
        )

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        """트랜잭션이 포함된 세션 (쓰기 작업용)"""
        session: AsyncSession = self._session_factory()
        token = _session_context.set(session)
        try:
            async with session.begin():  # 트랜잭션 시작
                yield session
                # 정상 완료 시 자동 commit
        except Exception as ex:
            logger.exception("Session rollback because of exception")
            raise ex 
        finally:
            _session_context.reset(token)
            await session.close()

    @asynccontextmanager
    async def test_session(self) -> AsyncGenerator[AsyncSession, None]:
        """테스트용 롤백 세션 (모든 변경사항이 롤백됨)"""
        session: AsyncSession = self._session_factory()
        token = _session_context.set(session)
        
        try:
            # 트랜잭션 시작
            transaction = await session.begin()
            yield session
            # 테스트 완료 후 무조건 롤백
            await transaction.rollback()
        except Exception as ex:
            logger.exception("Test session exception")
            # 이미 롤백됨
            raise ex
        finally:
            _session_context.reset(token)
            await session.close()
    
    def get_current_session(self) -> AsyncSession:
        try:
            session = _session_context.get()
            if session is None:
                raise LookupError("No session in context")
            return session
        except LookupError:
            raise APIException(ErrorCode.DATABASE_ERROR)

    async def close(self) -> None:
        """엔진 종료"""
        if self._engine:
            await self._engine.dispose()
            logger.info("Database engine disposed")

def transactional(func: Callable[..., Awaitable]) -> Callable[..., Awaitable]:
    """
    비동기 트랜잭션 데코레이터
    - test 환경: 통합 테스트용, 실제 DB의 test_session 사용
    - unit 환경: 유닛 테스트용, DB 없이 목(mock) 사용하므로 데코레이터 우회
    - local/prod: 실제 환경
    """
    @functools.wraps(func)
    async def _wrapper(*args, **kwargs) -> Any:
        environment = os.getenv('DB_SESSION', 'local').lower()

        # 유닛 테스트 환경: DB 없이 그냥 함수 실행 (mock repository 사용)
        if environment == 'unit':
            return await func(*args, **kwargs)

        if database_instance is None:
            logger.info("DB 인스턴스가 없습니다.")
            raise APIException(ErrorCode.DATABASE_ERROR)

        is_test_env = environment == 'test'
        if is_test_env:
            # 테스트 환경에서는 기존 세션 사용, savepoint 없이 flush만
            try:
                session = database_instance.get_current_session()
                try:
                    result = await func(*args, **kwargs)
                    await session.flush()  # 변경사항을 flush하여 조회 가능하게 함
                    logger.info("테스트 환경: flush 완료 (롤백은 테스트 종료시)")
                    return result
                except APIException as e:
                    # APIException은 그대로 전파 (비즈니스 로직 에러)
                    logger.info(f"테스트 환경: 비즈니스 로직 에러 발생 - {e}")
                    raise e
                except Exception as e:
                    # 기타 예외는 DATABASE_ERROR로 래핑
                    logger.exception("테스트 환경: 예기치 않은 에러 발생")
                    raise APIException(ErrorCode.DATABASE_ERROR)
            except LookupError:
                logger.info("테스트 환경: 세션이 없어서 새 세션 생성 불가, 에러 발생")
                raise APIException(ErrorCode.DATABASE_ERROR)

        else:
            # 로컬/프로덕션 환경: 기존 세션 확인 후 새 세션 생성
            try:
                current_session = database_instance.get_current_session()
                return await func(*args, **kwargs)
            except (LookupError, APIException):
                async with database_instance.session() as session:
                    return await func(*args, **kwargs)

    return _wrapper

# 호환성을 위한 별칭
async_transactional = transactional

# Global database instance
database_instance: Database|None = None