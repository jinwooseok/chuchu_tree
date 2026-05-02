"""이벤트 핸들러 자동 등록 데코레이터"""

import logging
import inspect
from typing import get_type_hints
from pydantic import BaseModel

from app.common.infra.event.in_memory_event_bus import get_event_bus

logger = logging.getLogger(__name__)

def camel_to_snake(name: str) -> str:
    """CamelCase를 snake_case로 변환"""
    import re
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()


def event_handler(event_types: str | list[str]):
    """
    메서드를 하나 이상의 이벤트 핸들러로 마킹

    사용:
        @event_handler(EventType.MEMBER_LOGGED_IN)
        async def update_last_login(self, command):
            ...

        @event_handler([EventType.MEMBER_LOGGED_IN, EventType.MEMBER_REGISTERED])
        async def update_member_activity(self, command):
            ...
    """
    def decorator(method):
        if isinstance(event_types, str):
            method._event_types = [event_types]
        else:
            method._event_types = event_types
        return method
    return decorator


def event_register_handlers(service_name: str | None = None):
    """
    Application Service의 @event_handler 메서드들을 자동으로 등록

    사용:
        @event_register_handlers()
        class AdvertiserApplicationService:
            @event_handler(EventType.MEMBER_LOGGED_IN)
            async def update_last_login(self, command):
                ...

    동작:
        1. 클래스의 모든 메서드 스캔
        2. _event_types 속성이 있는 메서드만 처리
    """
    def class_decorator(cls):
        actual_service_name = service_name or camel_to_snake(cls.__name__)

        # 최적화: _event_types 속성 있는 메서드만 스캔
        for method_name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
            if not hasattr(method, '_event_types'):
                continue

            event_types = method._event_types # type: ignore

            for event_type in event_types:
                def make_handler(bound_method, bound_service_name, bound_method_name):
                    """
                    메서드를 감싸는 wrapper 생성

                    wrapper의 책임:
                    1. dict → B_Command 변환 (타입 힌트 기반)
                    2. 실제 메서드 실행
                    3. B_Query → dict 변환
                    """
                    # 타입 힌트 미리 분석 (정적 분석 - 한 번만 실행)
                    try:
                        type_hints = get_type_hints(bound_method)
                    except Exception as e:
                        logger.warning(f"Failed to get type hints for {bound_method.__name__}: {e}")
                        type_hints = {}

                    # self를 제외한 첫 번째 파라미터의 타입 찾기
                    target_command_type = None
                    sig = inspect.signature(bound_method)
                    param_names = list(sig.parameters.keys())

                    if len(param_names) > 1:  # self 제외하고 파라미터가 있으면
                        second_param_name = param_names[1]
                        target_command_type = type_hints.get(second_param_name)

                    async def wrapper(event_name: str, payload: dict):
                        """
                        이벤트 핸들러 wrapper
                        """
                        try:
                            # Container에서 서비스 인스턴스 획득
                            from app.main import app
                            container = app.container
                            service = getattr(container, bound_service_name)()

                            # [2단계: dict → B_Command] wrapper의 책임
                            converted_payload = payload

                            if target_command_type is not None:
                                try:
                                    if isinstance(payload, dict):
                                        if inspect.isclass(target_command_type) and issubclass(target_command_type, BaseModel):
                                            converted_payload = target_command_type.model_validate(payload)
 
                                except TypeError:
                                    # Union type 등으로 issubclass 실패 시 원본 사용
                                    logger.debug(f"[wrapper] Type conversion skipped for {bound_method_name}")

                            # 실제 도메인 로직 실행
                            result = await bound_method(service, converted_payload)

                            # [3단계: B_Query → dict] wrapper의 책임
                            if hasattr(result, "model_dump"):
                                dict_result = result.model_dump()
                                return dict_result

                            return result

                        except Exception as e:
                            logger.error(
                                f"Error in event wrapper [{event_name}] "
                                f"for {bound_service_name}.{bound_method_name}: {e}",
                                exc_info=True
                            )
                            raise

                    return wrapper

                # wrapper 생성
                handler = make_handler(method, actual_service_name, method_name)

                # 전역 싱글톤 EventBus의 맵에 등록
                event_bus = get_event_bus()
                event_bus.subscribe(event_name=event_type)(handler)
                
                logger.info(
                    f"✨ [Event-Register] {actual_service_name}.{method_name} "
                    f"is now listening to '{event_type}'"
                )

        return cls
    return class_decorator
