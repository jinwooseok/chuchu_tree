"""Local Event Handler (fastapi-events 방식)"""

import logging
import re
from typing import Callable, Awaitable, Dict, List

logger = logging.getLogger(__name__)


class LocalEventHandler:
    """
    로컬 이벤트 핸들러
    """

    def __init__(self):
        # 이벤트명 → 핸들러 함수 매핑
        self._handlers: Dict[str, List[Callable[[str, dict | object], Awaitable[None]]]] = {}
        # 패턴 → 핸들러 함수 매핑 (COMMENT* 같은 패턴)
        self._pattern_handlers: List[tuple[str, Callable[[str, dict | object], Awaitable[None]]]] = []

    def register(self, event_name: str):
        """
        핸들러 등록 데코레이터

        Args:
            event_name: 이벤트 이름 또는 패턴 (예: "CREATE_COMMENT", "COMMENT*")

        Returns:
            데코레이터 함수
        """
        def decorator(handler_func: Callable[[str, dict | object], Awaitable[None]]):
            # 패턴인지 확인 (* 포함)
            if '*' in event_name:
                self._pattern_handlers.append((event_name, handler_func))
                logger.info(
                    f"✅ Registered pattern handler: {event_name} -> {handler_func.__name__}"
                )
            else:
                if event_name not in self._handlers:
                    self._handlers[event_name] = []

                self._handlers[event_name].append(handler_func)
                logger.info(
                    f"✅ Registered handler: {event_name} -> {handler_func.__name__}"
                )

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

    async def dispatch(
        self,
        event_name: str,
        payload: dict | object,
        wait: bool = True,
        ignore_errors: bool = False
    ) -> None:
        """
        이벤트 즉시 발행

        Args:
            event_name: 이벤트 이름
            payload: Payload (dict 또는 Command 객체)
            wait: True면 모든 핸들러 완료 대기 (기본: True)
            ignore_errors: True면 핸들러 에러 무시하고 계속 진행 (기본: False)

        Raises:
            Exception: ignore_errors=False일 때 핸들러에서 발생한 첫 번째 에러
        """
        # 1. 정확히 일치하는 핸들러 찾기
        handlers = self._handlers.get(event_name, [])

        # 2. 패턴 매칭 핸들러 찾기
        pattern_handlers = self._match_pattern(event_name)

        all_handlers = handlers + pattern_handlers

        if not all_handlers:
            logger.warning(f"No handlers registered for event: {event_name}")
            return

        logger.info(f"📤 Dispatching event '{event_name}' to {len(all_handlers)} handlers (wait={wait}, ignore_errors={ignore_errors})")

        # 3. 모든 핸들러 실행
        for handler in all_handlers:
            try:
                await handler(event_name, payload)
                logger.debug(f"✅ Handler {handler.__name__} executed for {event_name}")
            except Exception as e:
                logger.error(
                    f"❌ Handler {handler.__name__} failed for {event_name}: {e}",
                    exc_info=True
                )

                if not ignore_errors:
                    # 에러를 즉시 전파 (트랜잭션 롤백됨)
                    raise

                # ignore_errors=True면 다른 핸들러 계속 실행

    def get_registered_handlers(self) -> Dict[str, List[str]]:
        """등록된 핸들러 목록 반환 (디버깅용)"""
        result = {}

        for event_name, handlers in self._handlers.items():
            result[event_name] = [h.__name__ for h in handlers]

        for pattern, handler in self._pattern_handlers:
            if pattern not in result:
                result[pattern] = []
            result[pattern].append(f"{handler.__name__} (pattern)")

        return result


# 전역 인스턴스 (fastapi-events의 local_handler와 동일)
local_handler = LocalEventHandler()
