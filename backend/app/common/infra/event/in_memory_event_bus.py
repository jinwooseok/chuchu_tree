import logging
import re
from typing import Callable, Dict, List, Type, TypeVar

from app.common.domain.entity.domain_event import DomainEvent, TPayload, TResult
from app.common.domain.service.event_publisher import DomainEventBus

logger = logging.getLogger()

# 전역 싱글톤 인스턴스
_global_event_bus: 'InMemoryEventBus | None' = None


class InMemoryEventBus(DomainEventBus):
    """
    In-Memory 이벤트 버스 구현체

    - 핸들러 등록 (subscribe)
    - 이벤트 발행 (publish)
    - 패턴 매칭
    - 결과 수집 및 타입 변환
    """

    def __init__(self):
        # 이벤트명 → 핸들러 함수 매핑
        self._handlers: Dict[str, List[Callable[[str, dict], any]]] = {}
        # 패턴 → 핸들러 함수 매핑 (COMMENT* 같은 패턴)
        self._pattern_handlers: List[tuple[str, Callable[[str, dict], any]]] = []

    def subscribe(self, event_name: str):
        """
        핸들러 등록 데코레이터

        Args:
            event_name: 이벤트 이름 또는 패턴

        Returns:
            데코레이터 함수
        """
        def decorator(handler_func: Callable[[str, dict], any]):
            # 패턴인지 확인 (* 포함)
            if '*' in event_name:
                self._pattern_handlers.append((event_name, handler_func))
            else:
                if event_name not in self._handlers:
                    self._handlers[event_name] = []

                self._handlers[event_name].append(handler_func)

            return handler_func

        return decorator

    def _match_pattern(self, event_name: str) -> List[Callable]:
        """패턴 매칭 핸들러 찾기"""
        matched_handlers = []

        for pattern, handler in self._pattern_handlers:
            # * 를 정규식으로 변환
            regex_pattern = pattern.replace('*', '.*')
            if re.match(f'^{regex_pattern}$', event_name):
                matched_handlers.append(handler)

        return matched_handlers

    def _get_handlers(self, event_name: str) -> List[Callable]:
        """이벤트에 매칭되는 모든 핸들러 조회 (패턴 포함)"""
        handlers = self._handlers.get(event_name, []).copy()
        pattern_handlers = self._match_pattern(event_name)
        return handlers + pattern_handlers

    async def publish(
        self,
        event: DomainEvent[TPayload, TResult],
        ignore_errors: bool = False
    ) -> TResult | None:
        """
        도메인 이벤트 발행

        Event도 응답을 가질 수 있습니다 (Synchronous Event)
        - event.result_type이 None이면: Fire-and-Forget
        - event.result_type이 지정되면: 결과 수집 및 자동 변환

        Args:
            event: 도메인 이벤트 (result_type이 포함됨)
            ignore_errors: True면 핸들러 에러 무시 (기본: False)

        Returns:
            - event.result_type=None: None (Fire-and-Forget)
            - event.result_type 지정: 변환된 결과 객체 (TResult 타입)

        데이터 흐름:
        1. Request Mapping: A의 Pydantic 객체 -> dict (EventBus 책임)
        2. Handler 실행: dict -> B의 Pydantic 객체 -> B의 Query -> dict (wrapper 책임)
        3. Response Mapping: dict -> A의 Result 객체 (EventBus 책임)

        에러 처리:
        - ignore_errors=False: 핸들러 에러 시 즉시 예외 발생 (트랜잭션 롤백)
        - ignore_errors=True: 핸들러 에러 무시하고 다음 핸들러 계속 실행
        """
        event_name = event.event_type
        expects_result = event.expects_result()

        # [1단계: REQUEST MAPPING] A의 Pydantic 객체 -> dict (도메인 경계 분리)
        payload = event.data.model_dump() if hasattr(event.data, "model_dump") else event.data

        # 핸들러 찾기
        matched_handlers = self._get_handlers(event_name)

        if not matched_handlers:
            logger.warning(f"No handlers registered for event: {event_name}")
            return None

        # [2단계: 핸들러 실행] wrapper가 dict ↔ B 변환 담당
        results = []
        for handler in matched_handlers:
            try:
                result = await handler(event_name, payload)

                if expects_result:
                    results.append(result)

            except Exception as e:
                logger.error(
                    f"Handler {handler.__name__} failed for {event_name}: {e}",
                    exc_info=True
                )

                if not ignore_errors:
                    raise

        # Fire-and-Forget이면 여기서 종료
        if not expects_result:
            return None

        # [3단계: RESPONSE MAPPING] dict -> A의 Result 객체
        if event.result_type and results and results[0] is not None:
            raw_result = results[0]

            # wrapper가 dict로 반환했으므로 event.result_type으로 재조립
            if isinstance(raw_result, dict):
                return event.result_type.model_validate(raw_result)
            elif hasattr(raw_result, "model_dump"):
                return event.result_type.model_validate(raw_result.model_dump())
            else:
                return raw_result

        return None

def get_event_bus() -> InMemoryEventBus:
    """
    전역 싱글톤 EventBus 인스턴스 반환

    데코레이터에서 사용하기 위한 전역 접근 함수
    애플리케이션 전체에서 단일 EventBus 인스턴스를 공유합니다.

    Returns:
        InMemoryEventBus: 전역 싱글톤 인스턴스
    """
    global _global_event_bus
    if _global_event_bus is None:
        _global_event_bus = InMemoryEventBus()
        logger.info("Global EventBus singleton created")
    return _global_event_bus