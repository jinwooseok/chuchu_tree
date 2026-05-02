from abc import ABC, abstractmethod
from datetime import date

from app.common.domain.entity.system_log import SystemLog
from app.common.domain.enums import SystemLogType, SystemLogStatus
from app.common.domain.vo.identifiers import BaekjoonAccountId


class SystemLogRepository(ABC):

    @abstractmethod
    async def save(self, log: SystemLog) -> SystemLog:
        pass

    @abstractmethod
    async def find_by_type(self, log_type: SystemLogType) -> list[SystemLog]:
        pass

    @abstractmethod
    async def find_by_type_and_status(
        self,
        log_type: SystemLogType,
        status: SystemLogStatus,
    ) -> list[SystemLog]:
        pass

    @abstractmethod
    async def find_scheduler_success_dates_by_bj_account(
        self,
        bj_account_id: BaekjoonAccountId,
    ) -> set[date]:
        """SCHEDULER 타입 SUCCESS 로그에서 bj_account_id 기준 날짜 집합 반환.
        GetSchedulerInactivePeriodsUsecase 에서 사용."""
        pass
