from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.study.application.command.study_command import GetMyNoticesCommand
from app.study.application.query.notice_query import NoticeQuery
from app.study.domain.repository.notice_repository import NoticeRepository


class GetMyNoticesUsecase:
    def __init__(self, notice_repository: NoticeRepository):
        self.notice_repository = notice_repository

    @transactional(readonly=True)
    async def execute(self, command: GetMyNoticesCommand) -> list[NoticeQuery]:
        notices = await self.notice_repository.find_by_recipient(
            UserAccountId(command.requester_user_account_id), limit=50
        )
        return [
            NoticeQuery(
                notice_id=n.notice_id.value,
                category=n.category.value,
                is_read=n.is_read,
                created_at=n.created_at.isoformat(),
                content=n.content,
            )
            for n in notices
        ]
