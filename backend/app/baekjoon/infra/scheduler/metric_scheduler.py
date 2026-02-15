import asyncio
import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.baekjoon.application.usecase.update_bj_account_usecase import UpdateBjAccountUsecase
from app.core.database import get_global_database, set_database_context, reset_database_context
from app.core.exception import APIException

logger = logging.getLogger(__name__)


class BjAccountUpdateScheduler:
    """메트릭 수집 스케줄러"""
    
    def __init__(self, update_bj_account_use_case: UpdateBjAccountUsecase):
        self.update_bj_account_use_case = update_bj_account_use_case
        self.scheduler = AsyncIOScheduler()
        
    def start(self):
        """스케줄러 시작"""
        try:
            # 매일 6시 반에 수집 작업 스케줄링
            self.scheduler.add_job(
                self._collect_metrics_job,
                trigger=CronTrigger(hour=6, minute=30),
                id='daily_metric_collection',
                name='Daily Metrics Collection',
                replace_existing=True,
                max_instances=1  # 동시 실행 방지
            )
            
            self.scheduler.start()
            logger.info("Metric scheduler started successfully")
            
        except Exception as e:
            logger.error(f"Failed to start metric scheduler: {e}")
            raise
    
    def stop(self):
        """스케줄러 중지"""
        if self.scheduler.running:
            self.scheduler.shutdown(wait=True)
            logger.info("Metric scheduler stopped")
    
    async def _collect_metrics_job(self):
        """메트릭 수집 작업"""
        db = get_global_database()
        token = set_database_context(db)
        try:
            logger.info("Starting daily metric collection...")

            # 메트릭 수집 실행
            await self.update_bj_account_use_case.execute_bulk()


        except APIException as e:
            logger.error(f"API exception during metric collection: {e}")

        except Exception as e:
            logger.error(f"Unexpected error during metric collection: {e}")
            # 필요시 알림 시스템에 에러 전송
        finally:
            reset_database_context(token)
    
    async def collect_metrics_now(self) -> None:
        """즉시 메트릭 수집 (테스트용)"""
        await self._collect_metrics_job()


# 전역 스케줄러 인스턴스
_metric_scheduler: BjAccountUpdateScheduler|None = None


def init_metric_scheduler(service_metric_service: UpdateBjAccountUsecase) -> BjAccountUpdateScheduler:
    """메트릭 스케줄러 초기화"""
    global _metric_scheduler
    _metric_scheduler = BjAccountUpdateScheduler(service_metric_service)
    return _metric_scheduler


def get_metric_scheduler() -> BjAccountUpdateScheduler:
    """메트릭 스케줄러 인스턴스 반환"""
    if _metric_scheduler is None:
        raise RuntimeError("Metric scheduler not initialized")
    return _metric_scheduler


def start_scheduler():
    """스케줄러 시작"""
    if _metric_scheduler:
        _metric_scheduler.start()
    else:
        logger.error("Metric scheduler not initialized")


def stop_scheduler():
    """스케줄러 중지"""
    if _metric_scheduler:
        _metric_scheduler.stop()