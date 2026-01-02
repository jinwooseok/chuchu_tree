import json
import logging
from typing import Any, Optional, Union, List
from datetime import timedelta

import redis.asyncio as aioredis
from redis.asyncio import client
from redis.asyncio.connection import ConnectionPool
from redis.exceptions import ConnectionError, TimeoutError, RedisError

from app.config.settings import get_settings

logger = logging.getLogger(__name__)
class AsyncRedisClient:
    """비동기 Redis 클라이언트 래퍼 클래스"""
    
    def __init__(self, settings):
        self.settings = settings
        self._pool: Optional[ConnectionPool] = None
        self._pubsub_pool: Optional[ConnectionPool] = None  # PubSub 전용 풀
        self._client: Optional[aioredis.Redis] = None
        self._pubsub_client: Optional[aioredis.Redis] = None  # PubSub 전용 클라이언트
        self.redis_url = f"redis://:{self.settings.REDIS_PASSWORD}@{self.settings.REDIS_HOST}:{self.settings.REDIS_BINDING_PORT}"
        
    async def _initialize_client(self):
        """Redis 클라이언트 초기화"""
        try:
            # 일반 Connection Pool 생성
            self._pool = ConnectionPool(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_BINDING_PORT,
                password=self.settings.REDIS_PASSWORD,
                db=self.settings.REDIS_DB,
                decode_responses=True,
                max_connections=self.settings.REDIS_MAX_CONNECTIONS,
                retry_on_timeout=False,  # 무한 재시도 비활성화
                socket_timeout=self.settings.REDIS_SOCKET_TIMEOUT,
                socket_connect_timeout=self.settings.REDIS_CONNECT_TIMEOUT,
                health_check_interval=self.settings.REDIS_HEALTH_CHECK_INTERVAL,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            
            # PubSub 전용 Connection Pool 생성
            self._pubsub_pool = ConnectionPool(
                host=self.settings.REDIS_HOST,
                port=self.settings.REDIS_BINDING_PORT,
                password=self.settings.REDIS_PASSWORD,
                db=self.settings.REDIS_DB,
                decode_responses=True,
                max_connections=3000, 
                retry_on_timeout=False,  # 무한 재시도 비활성화
                socket_timeout=None,  # PubSub은 메시지를 무한정 기다려야 하므로 None
                socket_connect_timeout=self.settings.REDIS_CONNECT_TIMEOUT,
                health_check_interval=self.settings.REDIS_HEALTH_CHECK_INTERVAL,
                socket_keepalive=True,
                socket_keepalive_options={}
            )
            
            # Redis 클라이언트 생성
            self._client = aioredis.Redis(connection_pool=self._pool)
            self._pubsub_client = aioredis.Redis(connection_pool=self._pubsub_pool)
            
            # 연결 테스트
            await self._client.ping()
            await self._pubsub_client.ping()
            logger.info("Async Redis 연결 성공")
            
        except (ConnectionError, TimeoutError) as e:
            logger.error(f"Async Redis 연결 실패: {e}")
            raise e
    
    async def get_client(self) -> aioredis.Redis:
        """Redis 클라이언트 반환 (비동기)"""
        if self._client is None:
            await self._initialize_client()
        
        if self._client is None:
            raise RedisError("Failed to initialize Redis client")
        
        return self._client
    
    async def get_pubsub_client(self) -> aioredis.Redis:
        """PubSub 전용 클라이언트 반환"""
        if self._pubsub_client is None:
            await self._initialize_client()
        
        if self._pubsub_client is None:
            raise RedisError("Failed to initialize PubSub Redis client")
        
        return self._pubsub_client
    
    # ... 기존 메소드들 유지 (set, get, delete 등) ...
    
    async def publish(self, topic: str, message) -> None:
        """메시지 발행"""
        try:
            logger.info(f"Publishing to topic: {topic}")
            client = await self.get_client()
            
            # 메시지가 dict나 객체면 JSON으로 직렬화
            if not isinstance(message, str):
                message = json.dumps(message, ensure_ascii=False)
            
            result = await client.publish(topic, message)
            logger.info(f"Published to {topic}, subscribers: {result}")
            
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            raise

    async def subscribe(self, topic: str) -> client.PubSub:
        """채널 구독 - 매번 새로운 PubSub 인스턴스 생성"""
        try:
            logger.info(f"Subscribing to topic: {topic}")
            pubsub_client = await self.get_pubsub_client()
            
            # 매번 새로운 PubSub 인스턴스 생성
            pubsub = pubsub_client.pubsub()
            await pubsub.subscribe(topic)
            
            logger.info(f"Successfully subscribed to {topic}")
            return pubsub
            
        except Exception as e:
            logger.error(f"Failed to subscribe to {topic}: {e}")
            raise

    async def unsubscribe(self, pubsub: client.PubSub, topic: str) -> None:
        """채널 구독 해제"""
        try:
            await pubsub.unsubscribe(topic)
            await pubsub.close()
            logger.info(f"Unsubscribed from {topic}")
        except Exception as e:
            logger.error(f"Failed to unsubscribe from {topic}: {e}")
            
    async def set(
        self, 
        key: str, 
        value: Any, 
        ex: Optional[Union[int, timedelta]] = None,
        px: Optional[Union[int, timedelta]] = None,
        nx: bool = False,
        xx: bool = False
    ) -> bool:
        """
        키-값 저장 (비동기)
        
        Args:
            key: Redis 키
            value: 저장할 값 (자동으로 JSON 직렬화)
            ex: 만료 시간 (초 또는 timedelta)
            px: 만료 시간 (밀리초 또는 timedelta)
            nx: 키가 존재하지 않을 때만 설정
            xx: 키가 존재할 때만 설정
        """
        try:
            client = await self.get_client()
            # 값이 문자열이 아니면 JSON으로 직렬화
            if not isinstance(value, str):
                value = json.dumps(value, ensure_ascii=False)

            result = await client.set(key, value, ex=ex, px=px, nx=nx, xx=xx)
            return bool(result) if result is not None else False

        except RedisError as e:
            logger.error(f"Redis SET 오류 - key: {key}, error: {e}")
            return False

    async def get(self, key: str) -> Optional[Any]:
        """
        키로 값 조회 (비동기)
        
        Args:
            key: Redis 키
            
        Returns:
            저장된 값 (JSON이면 자동으로 파싱)
        """
        try:
            client = await self.get_client()
            value = await client.get(key)

            if value is None:
                return None

            # JSON 파싱 시도
            try:
                return json.loads(value)
            except (json.JSONDecodeError, TypeError):
                # JSON이 아니면 원본 문자열 반환
                return value

        except RedisError as e:
            logger.error(f"Redis GET 오류 - key: {key}, error: {e}")
            return None

    async def delete(self, *keys: str) -> int:
        """키 삭제 (비동기)"""
        try:
            client = await self.get_client()
            result = await client.delete(*keys)
            return int(result) if result is not None else 0
        except RedisError as e:
            logger.error(f"Redis DELETE 오류 - keys: {keys}, error: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """키 존재 여부 확인 (비동기)"""
        try:
            client = await self.get_client()
            result = await client.exists(key)
            return bool(result) if result is not None else False
        except RedisError as e:
            logger.error(f"Redis EXISTS 오류 - key: {key}, error: {e}")
            return False

    async def expire(self, key: str, time: Union[int, timedelta]) -> bool:
        """키 만료 시간 설정 (비동기)"""
        try:
            client = await self.get_client()
            result = await client.expire(key, time)
            return bool(result) if result is not None else False
        except RedisError as e:
            logger.error(f"Redis EXPIRE 오류 - key: {key}, error: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """키의 남은 TTL 조회 (초) (비동기)"""
        try:
            client = await self.get_client()
            result = await client.ttl(key)
            return int(result) if result is not None else -1
        except RedisError as e:
            logger.error(f"Redis TTL 오류 - key: {key}, error: {e}")
            return -1

    async def incr(self, key: str, amount: int = 1) -> int:
        """키 값 증가 (비동기)"""
        try:
            client = await self.get_client()
            result = await client.incr(key, amount)
            return int(result) if result is not None else 0
        except RedisError as e:
            logger.error(f"Redis INCR 오류 - key: {key}, error: {e}")
            return 0

    async def decr(self, key: str, amount: int = 1) -> int:
        """키 값 감소 (비동기)"""
        try:
            client = await self.get_client()
            result = await client.decr(key, amount)
            return int(result) if result is not None else 0
        except RedisError as e:
            logger.error(f"Redis DECR 오류 - key: {key}, error: {e}")
            return 0

    async def flushdb(self) -> bool:
        """현재 DB의 모든 키 삭제 (비동기) - 개발용"""
        try:
            client = await self.get_client()
            result = await client.flushdb()
            return bool(result) if result is not None else False
        except RedisError as e:
            logger.error(f"Redis FLUSHDB 오류: {e}")
            return False

    async def keys(self, pattern: str = "*") -> List[str]:
        """패턴에 매칭되는 키 조회 (비동기) - 주의: 운영에서는 사용 금지"""
        try:
            client = await self.get_client()
            result = await client.keys(pattern)
            return list(result) if result else []
        except RedisError as e:
            logger.error(f"Redis KEYS 오류 - pattern: {pattern}, error: {e}")
            return []

    async def close(self):
        """연결 종료"""
        try:
            if self._client:
                await self._client.aclose()
            if self._pubsub_client:
                await self._pubsub_client.aclose()
            if self._pool:
                await self._pool.aclose()
            if self._pubsub_pool:
                await self._pubsub_pool.aclose()
            logger.info("Async Redis 연결 종료")
        except Exception as e:
            logger.error(f"Error closing Redis connections: {e}")