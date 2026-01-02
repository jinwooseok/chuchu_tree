from abc import ABC, abstractmethod
from app.common.domain.entity.domain_event import DomainEvent


class DomainEventHandler(ABC):
    """도메인 이벤트 핸들러 인터페이스"""

    @abstractmethod
    async def handle(self, event: DomainEvent) -> any:
        """
        이벤트 처리

        Returns:
            Any: 핸들러의 처리 결과 (없으면 None)
        """
        pass


class DomainEventBus(ABC):
    """이벤트 버스 인터페이스 (In-Memory)"""

    @abstractmethod
    async def publish(self, event: DomainEvent, wait_for_result: bool = False) -> list[any] | None:
        """
        이벤트 발행

        Args:
            event: 도메인 이벤트
            wait_for_result: True면 핸들러 결과를 수집해서 반환 (Mediator 모드)

        Returns:
            wait_for_result=True: 핸들러들의 결과 리스트
            wait_for_result=False: None (Fire-and-Forget)
        """
        pass