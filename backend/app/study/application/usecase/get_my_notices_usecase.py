from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.study.application.command.study_command import GetMyNoticesCommand
from app.study.application.query.notice_query import NoticeQuery
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


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

        # collect sender IDs for notices that have senderUserAccountId
        sender_ids = list({
            n.content["senderUserAccountId"]
            for n in notices
            if isinstance(n.content, dict) and "senderUserAccountId" in n.content
        })
        sender_map = {
            u.user_account_id: u
            for u in await self.user_search_repository.find_by_user_account_ids(sender_ids)
        } if sender_ids else {}

        result = []
        for n in notices:
            content = dict(n.content) if isinstance(n.content, dict) else n.content
            sender_id = content.get("senderUserAccountId") if isinstance(content, dict) else None
            if sender_id is not None:
                sender = sender_map.get(sender_id)
                profile_image = (sender.profile_image if sender else None) or DEFAULT_PROFILE_IMAGE_PATH
                content["profileImageUrl"] = await self.storage_gateway.generate_presigned_url(profile_image)
            result.append(
                NoticeQuery(
                    notice_id=n.notice_id.value,
                    category=n.category.value,
                    is_read=n.is_read,
                    created_at=n.created_at.isoformat(),
                    content=content,
                )
            )
        return result
