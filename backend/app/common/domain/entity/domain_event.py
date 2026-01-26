from datetime import datetime
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Type
from pydantic import BaseModel

# 타입 변수 정의
TPayload = TypeVar('TPayload', bound=BaseModel)
TResult = TypeVar('TResult', bound=BaseModel)


@dataclass
class DomainEvent(Generic[TPayload, TResult]):
    """
    도메인 이벤트
    
    사용 패턴:
    1. Fire-and-Forget Event: result_type=None (기본)
    2. Event with Response: result_type 지정
    """
    event_type: str
    data: TPayload
    result_type: Type[TResult] | None = None
    event_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))
    occurred_at: datetime = field(default_factory=datetime.now)

    def expects_result(self) -> bool:
        """이 이벤트가 결과를 기대하는지 여부"""
        return self.result_type is not None

    def to_dict(self) -> dict[str, any]:
        """이벤트를 딕셔너리로 변환"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'expects_result': self.expects_result(),
            'data': self.data.model_dump() if hasattr(self.data, 'model_dump') else self.data
        }