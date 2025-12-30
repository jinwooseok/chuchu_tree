from abc import ABC
from datetime import datetime
from dataclasses import dataclass, field


@dataclass
class DomainEvent(ABC):
    """도메인 이벤트 기본 클래스"""
    event_type: str
    data: dict
    event_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))
    occurred_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        self.event_type = self.event_type
    
    def to_dict(self) -> dict[str, any]:
        """이벤트를 딕셔너리로 변환"""
        return {
            'event_id': self.event_id,
            'event_type': self.event_type,
            'occurred_at': self.occurred_at.isoformat(),
            'data': self._get_event_data()
        }
    
    def _get_event_data(self) -> dict[str, any]:
        """각 이벤트별 데이터 반환 (하위 클래스에서 구현)"""
        return self.data