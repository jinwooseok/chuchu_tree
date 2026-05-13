from app.common.domain.entity.system_log import SystemLog
from app.common.domain.enums import SystemLogType, SystemLogStatus
from app.common.domain.vo.identifiers import SystemLogId
from app.common.infra.model.system_log import SystemLogModel


class SystemLogMapper:

    @staticmethod
    def to_entity(model: SystemLogModel) -> SystemLog:
        return SystemLog(
            system_log_id=SystemLogId(model.system_log_id),
            log_type=SystemLogType(model.log_type),
            status=SystemLogStatus(model.status),
            log_data=model.log_data,
            should_notify=model.should_notify,
            notification_data=model.notification_data,
            notification_sent=model.notification_sent,
            created_at=model.created_at,
        )

    @staticmethod
    def to_model(entity: SystemLog) -> SystemLogModel:
        model = SystemLogModel(
            log_type=entity.log_type.value,
            status=entity.status.value,
            log_data=entity.log_data,
            should_notify=entity.should_notify,
            notification_data=entity.notification_data,
            notification_sent=entity.notification_sent,
            created_at=entity.created_at,
        )
        if entity.system_log_id is not None:
            model.system_log_id = entity.system_log_id.value
        return model
