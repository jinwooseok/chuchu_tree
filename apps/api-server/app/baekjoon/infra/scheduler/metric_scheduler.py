import logging
from datetime import date

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from app.baekjoon.application.usecase.update_bj_account_usecase import UpdateBjAccountUsecase
from app.common.domain.entity.system_log import SystemLog
from app.common.domain.entity.system_log_data import WeeklyUpdateLogData
from app.common.domain.enums import SystemLogType, SystemLogStatus
from app.common.domain.repository.system_log_repository import SystemLogRepository
from app.core.database import get_global_database, set_database_context, reset_database_context
from app.core.exception import APIException
from app.problem.application.service.problem_metadata_sync_service import ProblemMetadataSyncService

logger = logging.getLogger(__name__)


class BjAccountUpdateScheduler:
    """메트릭 수집 스케줄러"""

    def __init__(
        self,
        update_bj_account_use_case: UpdateBjAccountUsecase,
        problem_metadata_sync_service: ProblemMetadataSyncService,
        system_log_repository: SystemLogRepository | None = None,
    ):
        self.update_bj_account_use_case = update_bj_account_use_case
        self.problem_metadata_sync_service = problem_metadata_sync_service
        self.system_log_repository = system_log_repository
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """스케줄러 시작"""
        try:
            # 매일 23:55에 BJ 계정 메트릭 수집
            self.scheduler.add_job(
                self._collect_metrics_job,
                trigger=CronTrigger(hour=23, minute=55),
                id='daily_metric_collection',
                name='Daily Metrics Collection',
                replace_existing=True,
                max_instances=1  # 동시 실행 방지
            )

            # 매주 수요일 16:29에 문제/태그 데이터 업데이트
            self.scheduler.add_job(
                self._weekly_problem_update_job,
                trigger=CronTrigger(day_of_week='wed', hour=16, minute=54),
                id='weekly_problem_update',
                name='Weekly Problem/Tag Update',
                replace_existing=True,
                max_instances=1
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
        """메트릭 수집 작업 (scheduler_log는 usecase 내부에서 기록)"""
        db = get_global_database()
        token = set_database_context(db)
        try:
            logger.info("Starting daily metric collection...")
            await self.update_bj_account_use_case.execute_bulk()
            logger.info("Daily metric collection completed")

        except APIException as e:
            logger.error(f"API exception during metric collection: {e}")

        except Exception as e:
            logger.error(f"Unexpected error during metric collection: {e}")
        finally:
            reset_database_context(token)

    async def _weekly_problem_update_job(self):
        """
        주간 문제/태그 데이터 업데이트 작업

        ProblemMetadataSyncService.sync_all()을 호출해 앱 내부에서
        solved.ac 전체 태그·문제 데이터를 DB와 동기화한다.
        결과는 system_log(WEEKLY_UPDATE)에 기록된다.
        """
        logger.info("Starting weekly problem/tag update...")
        db = get_global_database()
        token = set_database_context(db)

        synced_tags = 0
        synced_problems = 0
        error_msg: str | None = None
        overall_status = SystemLogStatus.FAILED

        try:
            result = await self.problem_metadata_sync_service.sync_all()
            synced_tags = result.tag_count
            synced_problems = result.problem_count
            overall_status = SystemLogStatus.SUCCESS
            logger.info(
                f"Weekly problem/tag update completed: "
                f"tags={synced_tags}, problems={synced_problems}"
            )

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Unexpected error during weekly problem update: {e}")

        finally:
            try:
                log = SystemLog.create(
                    log_type=SystemLogType.WEEKLY_UPDATE,
                    status=overall_status,
                    log_data=WeeklyUpdateLogData(
                        run_date=date.today().isoformat(),
                        synced_tag_count=synced_tags,
                        synced_problem_count=synced_problems,
                        error=error_msg,
                    ).to_dict(),
                    should_notify=(overall_status == SystemLogStatus.FAILED),
                )
                await self.problem_metadata_sync_service.save_sync_result_log(log)
            except Exception as log_err:
                logger.error(f"Failed to save weekly update system_log: {log_err}")
            reset_database_context(token)

    async def collect_metrics_now(self) -> None:
        """즉시 메트릭 수집 (테스트용)"""
        await self._collect_metrics_job()


# 전역 스케줄러 인스턴스
_metric_scheduler: BjAccountUpdateScheduler | None = None


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
