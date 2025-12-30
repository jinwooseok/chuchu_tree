"""Payload Schema Registry (fastapi-events 방식)"""

import logging
from typing import Type, Dict, Any, TypeVar
from pydantic import BaseModel

logger = logging.getLogger(__name__)

T = TypeVar('T', bound=BaseModel)
class PayloadSchemaRegistry:
    """
    Event Payload 스키마 등록 레지스트리

    fastapi-events의 payload_schema와 동일한 방식

    사용법:
        @payload_schema.register(event_name="CREATE_COMMENT")
        class CreateCommentPayload(BaseModel):
            comment_id: int
            user_id: int
    """

    def __init__(self):
        self._schemas: Dict[str, Type[BaseModel]] = {}

    def register(self, event_name: str):
        """
        Payload 스키마 등록 데코레이터

        Args:
            event_name: 이벤트 이름

        Returns:
            데코레이터 함수
        """
        def decorator(payload_class: Type[T]) -> Type[T]:
            if not issubclass(payload_class, BaseModel):
                raise ValueError(
                    f"Payload class must inherit from BaseModel: {payload_class}"
                )

            self._schemas[event_name] = payload_class
            logger.info(f"✅ Registered payload schema: {event_name} -> {payload_class.__name__}")

            return payload_class

        return decorator

    def get_schema(self, event_name: str) -> Type[BaseModel] | None:
        """등록된 Payload 스키마 조회"""
        return self._schemas.get(event_name)

    def validate_payload(self, event_name: str, payload: dict) -> BaseModel:
        """
        Payload 검증 및 변환

        Args:
            event_name: 이벤트 이름
            payload: 검증할 payload (dict)

        Returns:
            검증된 Pydantic 모델 인스턴스

        Raises:
            ValueError: 스키마가 등록되지 않았거나 검증 실패
        """
        schema = self.get_schema(event_name)

        if not schema:
            raise ValueError(f"No payload schema registered for event: {event_name}")

        try:
            return schema(**payload)
        except Exception as e:
            raise ValueError(
                f"Payload validation failed for {event_name}: {e}"
            ) from e

    def get_all_schemas(self) -> Dict[str, Type[BaseModel]]:
        """등록된 모든 스키마 반환 (디버깅용)"""
        return self._schemas.copy()


# 전역 인스턴스 (fastapi-events의 registry와 동일)
payload_schema = PayloadSchemaRegistry()
