"""스케줄러 미작동 구간 조회 Response"""

from datetime import date
from pydantic import BaseModel, Field

from app.baekjoon.application.query.scheduler_inactive_periods_query import SchedulerInactivePeriodsQuery


class InactivePeriodResponse(BaseModel):
    start_date: date = Field(..., alias="startDate")
    end_date: date = Field(..., alias="endDate")

    class Config:
        populate_by_name = True


class GetSchedulerInactivePeriodsResponse(BaseModel):
    bj_account_id: str = Field(..., alias="bjAccountId")
    inactive_periods: list[InactivePeriodResponse] = Field(..., alias="inactivePeriods")

    class Config:
        populate_by_name = True

    @classmethod
    def from_query(cls, query: SchedulerInactivePeriodsQuery) -> "GetSchedulerInactivePeriodsResponse":
        return cls(
            bj_account_id=query.bj_account_id,
            inactive_periods=[
                InactivePeriodResponse(
                    start_date=p.start_date,
                    end_date=p.end_date
                )
                for p in query.inactive_periods
            ]
        )
