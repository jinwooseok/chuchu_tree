"""SystemLog Repository 구현"""

from datetime import date
from typing import override

from sqlalchemy import and_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.entity.system_log import SystemLog
from app.common.domain.enums import SystemLogType, SystemLogStatus
from app.common.domain.repository.system_log_repository import SystemLogRepository
from app.common.domain.vo.identifiers import BaekjoonAccountId
from app.common.infra.mapper.system_log_mapper import SystemLogMapper
from app.common.infra.model.system_log import SystemLogModel
from app.core.database import Database


class SystemLogRepositoryImpl(SystemLogRepository):

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, log: SystemLog) -> SystemLog:
        model = SystemLogMapper.to_model(log)
        self.session.add(model)
        await self.session.flush()
        return SystemLogMapper.to_entity(model)

    @override
    async def find_by_type(self, log_type: SystemLogType) -> list[SystemLog]:
        stmt = select(SystemLogModel).where(
            SystemLogModel.log_type == log_type.value
        )
        result = await self.session.execute(stmt)
        return [SystemLogMapper.to_entity(m) for m in result.scalars().all()]

    @override
    async def find_by_type_and_status(
        self,
        log_type: SystemLogType,
        status: SystemLogStatus,
    ) -> list[SystemLog]:
        stmt = select(SystemLogModel).where(
            and_(
                SystemLogModel.log_type == log_type.value,
                SystemLogModel.status == status.value,
            )
        )
        result = await self.session.execute(stmt)
        return [SystemLogMapper.to_entity(m) for m in result.scalars().all()]

    @override
    async def find_scheduler_success_dates_by_bj_account(
        self,
        bj_account_id: BaekjoonAccountId,
    ) -> set[date]:
        stmt = select(
            text("DATE(JSON_UNQUOTE(JSON_EXTRACT(log_data, '$.run_date')))")
        ).where(
            and_(
                SystemLogModel.log_type == SystemLogType.SCHEDULER.value,
                SystemLogModel.status == SystemLogStatus.SUCCESS.value,
                text(
                    "JSON_UNQUOTE(JSON_EXTRACT(log_data, '$.bj_account_id')) = :bj_id"
                ).bindparams(bj_id=bj_account_id.value),
            )
        )
        result = await self.session.execute(stmt)
        return {row[0] for row in result.all() if row[0] is not None}
