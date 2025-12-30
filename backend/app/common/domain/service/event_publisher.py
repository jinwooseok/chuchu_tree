from abc import ABC, abstractmethod
from app.common.domain.entity.domain_event import DomainEvent


class DomainEventHandler(ABC):
    """도메인 이벤트 핸들러 인터페이스"""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> None:
        """이벤트 처리"""
        pass


class DomainEventBus(ABC):
    """이벤트 버스 인터페이스 (In-Memory)"""

    @abstractmethod
    async def publish(self, event: DomainEvent) -> None:
        """이벤트 발행"""
        pass