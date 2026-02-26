"""
system_log.log_data 필드의 타입별 구조 및 역직렬화 매퍼.

각 log_type에 대응하는 dataclass와 SystemLogDataMapper를 정의한다.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from app.common.domain.enums import SystemLogType


@dataclass
class FieldChange:
    """단일 필드 변경 이력 (메타데이터 업데이트에서 사용)"""
    field: str
    old_value: Any
    new_value: Any


@dataclass
class SchedulerLogData:
    """log_type=SCHEDULER 의 log_data 구조"""
    bj_account_id: str
    run_date: str            # ISO date string (YYYY-MM-DD)
    added_problem_ids: list[int]
    new_solved_count: int
    affected_user_ids: list[int]
    error: str | None

    def to_dict(self) -> dict:
        return {
            "bj_account_id": self.bj_account_id,
            "run_date": self.run_date,
            "added_problem_ids": self.added_problem_ids,
            "new_solved_count": self.new_solved_count,
            "affected_user_ids": self.affected_user_ids,
            "error": self.error,
        }


@dataclass
class RefreshLogData:
    """log_type=REFRESH 의 log_data 구조 (단일 유저 수동 갱신)"""
    bj_account_id: str
    requesting_user_account_id: int
    run_date: str            # ISO date string (YYYY-MM-DD)
    added_problem_ids: list[int]
    new_solved_count: int
    affected_user_ids: list[int]
    error: str | None

    def to_dict(self) -> dict:
        return {
            "bj_account_id": self.bj_account_id,
            "requesting_user_account_id": self.requesting_user_account_id,
            "run_date": self.run_date,
            "added_problem_ids": self.added_problem_ids,
            "new_solved_count": self.new_solved_count,
            "affected_user_ids": self.affected_user_ids,
            "error": self.error,
        }


@dataclass
class BulkUpdateLogData:
    """log_type=BULK_UPDATE 의 log_data 구조 (배치 입력)"""
    user_account_id: int
    bj_account_id: str
    # input_records: [["ISO datetime string", [problem_id, ...]], ...]
    input_records: list[list]
    added_problem_ids: list[int]
    affected_dates: list[str]     # ISO date strings
    skipped_problem_ids: list[int]
    error: str | None

    def to_dict(self) -> dict:
        return {
            "user_account_id": self.user_account_id,
            "bj_account_id": self.bj_account_id,
            "input_records": self.input_records,
            "added_problem_ids": self.added_problem_ids,
            "affected_dates": self.affected_dates,
            "skipped_problem_ids": self.skipped_problem_ids,
            "error": self.error,
        }


@dataclass
class MetadataUpdateLogData:
    """log_type=PROBLEM_METADATA 의 log_data 구조"""
    entity_type: str      # MetadataEntityType value
    entity_id: int
    changes: list[FieldChange]

    def to_dict(self) -> dict:
        return {
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "changes": [
                {"field": c.field, "old_value": c.old_value, "new_value": c.new_value}
                for c in self.changes
            ],
        }


@dataclass
class WeeklyUpdateLogData:
    """log_type=WEEKLY_UPDATE 의 log_data 구조 (주간 문제/태그 업데이트)"""
    run_date: str               # ISO date string (YYYY-MM-DD)
    synced_tag_count: int       # 처리된 태그 수
    synced_problem_count: int   # 처리된 문제 수
    error: str | None

    def to_dict(self) -> dict:
        return {
            "run_date": self.run_date,
            "synced_tag_count": self.synced_tag_count,
            "synced_problem_count": self.synced_problem_count,
            "error": self.error,
        }


@dataclass
class NotificationData:
    """notification_data 필드의 구조"""
    title: str
    message: str
    severity: str     # "INFO" | "WARNING" | "ERROR"

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "message": self.message,
            "severity": self.severity,
        }


class SystemLogDataMapper:
    """log_data dict → 타입별 객체로 역직렬화"""

    @staticmethod
    def parse(
        log_type: SystemLogType,
        log_data: dict[str, Any],
    ) -> SchedulerLogData | RefreshLogData | BulkUpdateLogData | MetadataUpdateLogData | WeeklyUpdateLogData:
        match log_type:
            case SystemLogType.SCHEDULER:
                return SchedulerLogData(
                    bj_account_id=log_data["bj_account_id"],
                    run_date=log_data["run_date"],
                    added_problem_ids=log_data.get("added_problem_ids", []),
                    new_solved_count=log_data.get("new_solved_count", 0),
                    affected_user_ids=log_data.get("affected_user_ids", []),
                    error=log_data.get("error"),
                )
            case SystemLogType.REFRESH:
                return RefreshLogData(
                    bj_account_id=log_data["bj_account_id"],
                    requesting_user_account_id=log_data["requesting_user_account_id"],
                    run_date=log_data["run_date"],
                    added_problem_ids=log_data.get("added_problem_ids", []),
                    new_solved_count=log_data.get("new_solved_count", 0),
                    affected_user_ids=log_data.get("affected_user_ids", []),
                    error=log_data.get("error"),
                )
            case SystemLogType.BULK_UPDATE:
                return BulkUpdateLogData(
                    user_account_id=log_data["user_account_id"],
                    bj_account_id=log_data.get("bj_account_id", ""),
                    input_records=log_data.get("input_records", []),
                    added_problem_ids=log_data.get("added_problem_ids", []),
                    affected_dates=log_data.get("affected_dates", []),
                    skipped_problem_ids=log_data.get("skipped_problem_ids", []),
                    error=log_data.get("error"),
                )
            case SystemLogType.PROBLEM_METADATA:
                changes = [
                    FieldChange(
                        field=c["field"],
                        old_value=c["old_value"],
                        new_value=c["new_value"],
                    )
                    for c in log_data.get("changes", [])
                ]
                return MetadataUpdateLogData(
                    entity_type=log_data["entity_type"],
                    entity_id=log_data["entity_id"],
                    changes=changes,
                )
            case SystemLogType.WEEKLY_UPDATE:
                return WeeklyUpdateLogData(
                    run_date=log_data["run_date"],
                    synced_tag_count=log_data.get("synced_tag_count", 0),
                    synced_problem_count=log_data.get("synced_problem_count", 0),
                    error=log_data.get("error"),
                )
            case _:
                raise ValueError(f"알 수 없는 log_type: {log_type}")

    @staticmethod
    def parse_notification(
        notification_data: dict[str, Any] | None,
    ) -> NotificationData | None:
        if notification_data is None:
            return None
        return NotificationData(
            title=notification_data["title"],
            message=notification_data["message"],
            severity=notification_data["severity"],
        )
