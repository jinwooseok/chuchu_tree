import logging

from app.common.domain.enums import NoticeCategory, NoticeCategoryDetail, SystemLogType
from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import ProblemId, UserAccountId
from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.study.application.command.notice_command import (
    CreateNoticeCommand,
    HandleBatchProblemsUpdatedCommand,
    HandleBjSyncedCommand,
)
from app.study.application.util.notice_message import generate_notice_message
from app.study.domain.entity.notice import Notice
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.study.infra.sse.notice_manager import NoticeSSEManager

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"

# category_detail → content 내 profileImageUrl 조회용 userAccountId 키
_PROFILE_ID_KEY: dict[str, str] = {
    "REQUESTED_STUDY_INVITATION": "inviterUserAccountId",
    "RESPONSED_STUDY_INVITATION": "inviteeUserAccountId",
    "REQUESTED_STUDY_APPLICATION": "applicantUserAccountId",
    "RESPONSED_STUDY_APPLICATION": "ownerUserAccountId",
    "ASSIGNED_STUDY_PROBLEM": "assignerUserAccountId",
}


def _notice_to_sse_payload(notice: Notice, profile_image_url: str | None = None) -> dict:
    detail = notice.category_detail.value if notice.category_detail else None
    content = dict(notice.content)
    if profile_image_url:
        content["profileImageUrl"] = profile_image_url
    return {
        "noticeId": notice.notice_id.value,
        "category": notice.category.value,
        "categoryDetail": detail,
        "isRead": notice.is_read,
        "createdAt": notice.created_at.isoformat(),
        "message": generate_notice_message(detail, notice.content),
        "content": content,
    }


@event_register_handlers()
class NoticeCreationService:
    def __init__(
        self,
        notice_repository: NoticeRepository,
        notice_sse_manager: NoticeSSEManager,
        problem_repository: ProblemRepository,
        user_search_repository: UserSearchRepository,
        storage_gateway: StorageGateway,
    ):
        self.notice_repository = notice_repository
        self.notice_sse_manager = notice_sse_manager
        self.problem_repository = problem_repository
        self.user_search_repository = user_search_repository
        self.storage_gateway = storage_gateway

    async def _get_profile_image_url(self, content: dict, category_detail: str | None) -> str | None:
        uid_key = _PROFILE_ID_KEY.get(category_detail or "")
        if not uid_key:
            return None
        uid = content.get(uid_key)
        if uid is None:
            return None
        user = await self.user_search_repository.find_by_user_account_id(uid)
        image_path = (user.profile_image if user else None) or DEFAULT_PROFILE_IMAGE_PATH
        return await self.storage_gateway.generate_presigned_url(image_path, expiry_seconds=21600)

    @event_handler("NOTICE_REQUESTED")
    @transactional
    async def handle_notice_requested(self, command: CreateNoticeCommand) -> None:
        try:
            notice = Notice.create(
                recipient_user_account_id=UserAccountId(command.recipient_user_account_id),
                category=NoticeCategory(command.category),
                category_detail=NoticeCategoryDetail(command.category_detail),
                content=command.content,
            )
            saved = await self.notice_repository.insert(notice)
            profile_image_url = await self._get_profile_image_url(command.content, command.category_detail)
            await self.notice_sse_manager.notify(
                command.recipient_user_account_id,
                "NOTICE",
                _notice_to_sse_payload(saved, profile_image_url),
            )
        except Exception as e:
            logger.error(f"[NoticeCreationService] NOTICE_REQUESTED 처리 실패: {e}")

    @event_handler("BJ_ACCOUNT_SYNCED")
    @transactional
    async def handle_bj_account_synced(self, command: HandleBjSyncedCommand) -> None:
        try:
            if command.log_type == SystemLogType.BULK_UPDATE.value:
                return

            if command.added_problem_ids:
                problems = await self.problem_repository.find_by_ids(
                    [ProblemId(pid) for pid in command.added_problem_ids]
                )
                summary = [{"problemId": p.problem_id.value, "problemTitle": p.title} for p in problems]
                updated_by = "DIRECT_REFRESH" if command.log_type == SystemLogType.REFRESH.value else command.log_type
                notice = Notice.create(
                    recipient_user_account_id=UserAccountId(command.user_account_id),
                    category=NoticeCategory.USER_PROBLEM,
                    category_detail=NoticeCategoryDetail.UPDATED_USER_PROBLEM,
                    content={"problemsByDate": [{"solvedDate": command.date, "problems": summary}], "updatedBy": updated_by},
                )
                saved = await self.notice_repository.insert(notice)
                await self.notice_sse_manager.notify(
                    command.user_account_id, "NOTICE", _notice_to_sse_payload(saved)
                )

            if command.new_tier_id is not None:
                notice = Notice.create(
                    recipient_user_account_id=UserAccountId(command.user_account_id),
                    category=NoticeCategory.USER_TIER,
                    category_detail=NoticeCategoryDetail.UPDATED_USER_TIER,
                    content={"tierLevel": command.new_tier_id, "updatedBy": updated_by, "updatedDate": command.date},
                )
                saved = await self.notice_repository.insert(notice)
                await self.notice_sse_manager.notify(
                    command.user_account_id, "NOTICE", _notice_to_sse_payload(saved)
                )
        except Exception as e:
            logger.error(f"[NoticeCreationService] BJ_ACCOUNT_SYNCED 처리 실패: {e}")

    @event_handler("BATCH_PROBLEMS_UPDATED")
    @transactional
    async def handle_batch_problems_updated(self, command: HandleBatchProblemsUpdatedCommand) -> None:
        try:
            if not command.problem_ids:
                return
            problems = await self.problem_repository.find_by_ids(
                [ProblemId(pid) for pid in command.problem_ids]
            )
            summary = [{"problemId": p.problem_id.value, "problemTitle": p.title} for p in problems]
            notice = Notice.create(
                recipient_user_account_id=UserAccountId(command.user_account_id),
                category=NoticeCategory.USER_PROBLEM,
                category_detail=NoticeCategoryDetail.UPDATED_USER_PROBLEM,
                content={"problemsByDate": [{"solvedDate": command.date, "problems": summary}], "updatedBy": "DIRECT_BATCH_UPDATE"},
            )
            saved = await self.notice_repository.insert(notice)
            await self.notice_sse_manager.notify(
                command.user_account_id, "NOTICE", _notice_to_sse_payload(saved)
            )
        except Exception as e:
            logger.error(f"[NoticeCreationService] BATCH_PROBLEMS_UPDATED 처리 실패: {e}")
