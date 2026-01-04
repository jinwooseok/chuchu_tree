from abc import ABC, abstractmethod
from app.common.domain.entity.domain_event import DomainEvent, TPayload, TResult


class DomainEventBus(ABC):
    """
    이벤트 버스 인터페이스

    Event도 응답을 가질 수 있습니다 (Synchronous Event / Request-Reply Event)
    """

    @abstractmethod
    async def publish(
        self,
        event: DomainEvent[TPayload, TResult],
        ignore_errors: bool = False
    ) -> TResult | None:
        """
        이벤트 발행

        Args:
            event: 도메인 이벤트 (result_type 포함)
            ignore_errors: True면 핸들러 에러 무시

        Returns:
            - event.result_type=None: None (Fire-and-Forget)
            - event.result_type 지정: 변환된 결과 객체
        """
        pass