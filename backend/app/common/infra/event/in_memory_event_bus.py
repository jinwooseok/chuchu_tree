import logging
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.entity.payload_schema import payload_schema
from app.common.domain.service.local_handler import LocalEventHandler

logger = logging.getLogger()


class InMemoryEventBus(DomainEventBus):
    """
    In-Memory 이벤트 버스 구현체
    """

    def __init__(self, local_handler: LocalEventHandler):
        self.local_handler = local_handler

    async def publish(
        self,
        event: DomainEvent,
        wait: bool = True,
        ignore_errors: bool = False
    ) -> None:
        """
        도메인 이벤트를 local_handler에 위임

        Domain Layer에서는 EventType을 사용하고,
        Infrastructure Layer에서 실제 처리

        Args:
            event: 도메인 이벤트
            wait: True면 모든 핸들러 완료 대기 (기본: True)
            ignore_errors: True면 핸들러 에러 무시 (기본: False)

        Payload 검증:
        - 스키마가 등록된 경우 자동으로 타입 검증
        - 등록 안 된 경우는 그대로 통과 (backward compatibility)

        에러 처리:
        - ignore_errors=False: 핸들러 에러 시 즉시 예외 발생 (트랜잭션 롤백)
        - ignore_errors=True: 핸들러 에러 무시하고 다음 핸들러 계속 실행
        """
        event_name = event.event_type
        payload = event.data

        # Payload 검증 (스키마가 등록되어 있으면)
        schema = payload_schema.get_schema(event_name)
        if schema:
            try:
                validated_payload = payload_schema.validate_payload(event_name, payload)
                payload = validated_payload
                
            except ValueError as e:
                raise
        else:
            logger.debug(f"⚠️ No schema registered for event: {event_name}, skipping validation")

        # local_handler에 위임 (fastapi-events 스타일)
        await self.local_handler.dispatch(
            event_name=event_name,
            payload=payload,
            wait=wait,
            ignore_errors=ignore_errors
        )

    def get_handlers_count(self, event_type: str) -> int:
        """특정 이벤트 타입의 핸들러 수 반환 (테스트용)"""
        handlers = self.local_handler._handlers.get(event_type, [])
        pattern_handlers = [h for p, h in self.local_handler._pattern_handlers if p == event_type]
        return len(handlers) + len(pattern_handlers)