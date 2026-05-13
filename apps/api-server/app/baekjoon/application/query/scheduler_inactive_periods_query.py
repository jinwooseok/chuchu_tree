"""스케줄러 미작동 구간 조회 Query"""

from dataclasses import dataclass, field
from datetime import date


@dataclass
class InactivePeriod:
    start_date: date
    end_date: date


@dataclass
class SchedulerInactivePeriodsQuery:
    bj_account_id: str
    inactive_periods: list[InactivePeriod] = field(default_factory=list)
