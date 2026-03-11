from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.study.application.command.study_command import GetMyNoticesCommand
from app.study.application.query.notice_query import NoticeQuery
from app.study.application.util.notice_message import generate_notice_message
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"

# 카테고리별 profileImageUrl 주입을 위한 userAccountId 키 매핑
PROFILE_ID_KEYS: dict[str, list[str]] = {
    "REQUESTED_STUDY_INVITATION": ["inviterUserAccountId"],
    "RESPONSED_STUDY_INVITATION": ["inviteeUserAccountId"],
    "REQUESTED_STUDY_APPLICATION": ["applicantUserAccountId"],
    "RESPONSED_STUDY_APPLICATION": ["ownerUserAccountId"],
    "ASSIGNED_STUDY_PROBLEM": ["assignerUserAccountId"],
}


class GetMyNoticesUsecase:
    def __init__(
        self,
        notice_repository: NoticeRepository,
        user_search_repository: UserSearchRepository,
        storage_gateway: StorageGateway,
    ):
        self.notice_repository = notice_repository
        self.user_search_repository = user_search_repository
        self.storage_gateway = storage_gateway

    @transactional(readonly=True)
    async def execute(self, command: GetMyNoticesCommand) -> list[NoticeQuery]:
        notices = await self.notice_repository.find_by_recipient(
            UserAccountId(command.requester_user_account_id), limit=50
        )

        # 모든 notice에서 profileImageUrl이 필요한 userAccountId 수집
        profile_user_ids: set[int] = set()
        for n in notices:
            if not isinstance(n.content, dict) or n.category_detail is None:
                continue
            detail = n.category_detail.value if hasattr(n.category_detail, "value") else str(n.category_detail)
            keys = PROFILE_ID_KEYS.get(detail, [])
            for key in keys:
                uid = n.content.get(key)
                if uid is not None:
                    profile_user_ids.add(uid)
            # ASSIGNED_STUDY_PROBLEM: assignees 목록의 userAccountId도 수집
            if detail == "ASSIGNED_STUDY_PROBLEM":
                for assignee in n.content.get("assignees", []):
                    uid = assignee.get("userAccountId")
                    if uid is not None:
                        profile_user_ids.add(uid)

        # 배치 조회
        user_map = {}
        if profile_user_ids:
            users = await self.user_search_repository.find_by_user_account_ids(list(profile_user_ids))
            user_map = {u.user_account_id: u for u in users}

        result = []
        for n in notices:
            content = dict(n.content) if isinstance(n.content, dict) else {}
            detail = None
            if n.category_detail is not None:
                detail = n.category_detail.value if hasattr(n.category_detail, "value") else str(n.category_detail)

            # profileImageUrl 주입
            if detail is not None:
                keys = PROFILE_ID_KEYS.get(detail, [])
                for key in keys:
                    uid = content.get(key)
                    if uid is not None:
                        user = user_map.get(uid)
                        profile_image = (user.profile_image if user else None) or DEFAULT_PROFILE_IMAGE_PATH
                        content["profileImageUrl"] = await self.storage_gateway.generate_presigned_url(profile_image, expiry_seconds=21600)
                        break

            # ASSIGNED_STUDY_PROBLEM: assignees 각각에 profileImageUrl 주입
            if detail == "ASSIGNED_STUDY_PROBLEM" and "assignees" in content:
                enriched_assignees = []
                for assignee in content["assignees"]:
                    uid = assignee.get("userAccountId")
                    user = user_map.get(uid) if uid is not None else None
                    profile_image = (user.profile_image if user else None) or DEFAULT_PROFILE_IMAGE_PATH
                    enriched_assignees.append({
                        **assignee,
                        "profileImageUrl": await self.storage_gateway.generate_presigned_url(profile_image, expiry_seconds=21600),
                    })
                content["assignees"] = enriched_assignees

            # 구 레코드 호환: senderUserAccountId 처리
            sender_id = content.get("senderUserAccountId") if detail is None else None
            if sender_id is not None and sender_id not in user_map:
                users = await self.user_search_repository.find_by_user_account_ids([sender_id])
                if users:
                    user_map[sender_id] = users[0]
            if sender_id is not None:
                sender = user_map.get(sender_id)
                profile_image = (sender.profile_image if sender else None) or DEFAULT_PROFILE_IMAGE_PATH
                content["profileImageUrl"] = await self.storage_gateway.generate_presigned_url(profile_image, expiry_seconds=21600)

            message = generate_notice_message(detail, content)

            result.append(
                NoticeQuery(
                    notice_id=n.notice_id.value,
                    category=n.category.value,
                    category_detail=detail,
                    is_read=n.is_read,
                    created_at=n.created_at.isoformat(),
                    message=message,
                    content=content,
                )
            )
        return result
