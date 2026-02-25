from dataclasses import dataclass
from datetime import datetime
from typing import Any

from app.common.domain.enums import SystemLogType, SystemLogStatus
from app.common.domain.vo.identifiers import SystemLogId


@dataclass
class SystemLog:
    """공통 시스템 로그 도메인 엔티티"""
    system_log_id: SystemLogId | None
    log_type: SystemLogType
    status: SystemLogStatus
    log_data: dict[str, Any]
    should_notify: bool
    notification_data: dict[str, Any] | None
    notification_sent: bool | None
    created_at: datetime

    @staticmethod
    def create(
        log_type: SystemLogType,
        status: SystemLogStatus,
        log_data: dict[str, Any],
        should_notify: bool,
        notification_data: dict[str, Any] | None = None,
    ) -> 'SystemLog':
        return SystemLog(
            system_log_id=None,
            log_type=log_type,
            status=status,
            log_data=log_data,
            should_notify=should_notify,
            notification_data=notification_data,
            notification_sent=None,
            created_at=datetime.now(),
        )
