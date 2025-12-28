"""이벤트 핸들러 자동 등록 데코레이터"""

import logging
import inspect
from typing import get_type_hints
from pydantic import BaseModel

from app.common.domain.service.local_handler import local_handler

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
                def make_handler(bound_method, bound_service_name):
                    async def wrapper(event_name: str, payload):
                        try:
                            from main import app
                            container = app.container
                            service = getattr(container, bound_service_name)()

                            # Command 객체 또는 dict 처리
                            type_hints = get_type_hints(bound_method)
                            params = list(type_hints.items())

                            if len(params) > 1:
                                param_name, param_type = params[1]
                                
                                # Union type 처리 (int | Command)
                                if hasattr(param_type, '__args__'):
                                    # Union type이면 BaseModel 찾기
                                    for arg_type in param_type.__args__:
                                        try:
                                            if isinstance(arg_type, type) and issubclass(arg_type, BaseModel):
                                                if isinstance(payload, arg_type):
                                                    result = await bound_method(service, payload)
                                                elif isinstance(payload, dict):
                                                    payload_obj = arg_type(**payload)
                                                    result = await bound_method(service, payload_obj)
                                                else:
                                                    result = await bound_method(service, payload)

                                                logger.info(f"✅ Event handler succeeded: {bound_service_name}.{bound_method.__name__} for {event_name}")
                                                return result
                                        except TypeError:
                                            # issubclass 실패 시 다음 arg로
                                            continue
                                # 단일 BaseModel type
                                try:
                                    if isinstance(param_type, type) and issubclass(param_type, BaseModel):
                                        if isinstance(payload, param_type):
                                            result = await bound_method(service, payload)
                                        elif isinstance(payload, dict):
                                            # dict를 Command로 변환
                                            payload_obj = param_type(**payload)
                                            result = await bound_method(service, payload_obj)
                                        else:
                                            result = await bound_method(service, payload)
                                        return result
                                except TypeError:
                                    # issubclass 실패 시 fallback
                                    pass

                            # fallback: dict를 그대로 전달
                            result = await bound_method(service, payload)
                            return result

                        except Exception as e:
                            raise
                    return wrapper

                handler = make_handler(method, actual_service_name)
                local_handler.register(event_name=event_type)(handler)
                logger.info(f"✅ Registered: {actual_service_name}.{method_name} → {event_type.value}")

        return cls
    return class_decorator
