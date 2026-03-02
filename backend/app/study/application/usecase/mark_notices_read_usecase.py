from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import MarkNoticesReadCommand
from app.study.domain.repository.notice_repository import NoticeRepository


class MarkNoticesReadUsecase:
    def __init__(self, notice_repository: NoticeRepository):
        self.notice_repository = notice_repository

    @transactional
    async def execute(self, command: MarkNoticesReadCommand) -> None:
        for notice_id in command.notice_ids:
            notice = await self.notice_repository.find_by_id(notice_id)
            if notice is None:
                continue
            if notice.recipient_user_account_id.value != command.requester_user_account_id:
                raise APIException(ErrorCode.NOTICE_NOT_FOR_ME)
            notice.mark_as_read()
            await self.notice_repository.update(notice)
