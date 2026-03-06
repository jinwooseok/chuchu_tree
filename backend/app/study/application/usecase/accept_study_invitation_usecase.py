from app.common.domain.vo.identifiers import StudyInvitationId, UserAccountId
from app.common.domain.enums import InvitationStatus, NoticeCategory
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import AcceptStudyInvitationCommand
from app.study.domain.entity.notice import Notice
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.study.infra.sse.notice_manager import NoticeSSEManager


class AcceptStudyInvitationUsecase:
    def __init__(
        self,
        invitation_repository: StudyInvitationRepository,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
        notice_repository: NoticeRepository,
        notice_sse_manager: NoticeSSEManager,
    ):
        self.invitation_repository = invitation_repository
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository
        self.notice_repository = notice_repository
        self.notice_sse_manager = notice_sse_manager

    @transactional
    async def execute(self, command: AcceptStudyInvitationCommand) -> None:
        invitation = await self.invitation_repository.find_by_id(
            StudyInvitationId(command.invitation_id)
        )
        if invitation is None:
            raise APIException(ErrorCode.INVITATION_NOT_FOUND)

        requester_id = UserAccountId(command.requester_user_account_id)
        if invitation.invitee_user_account_id.value != requester_id.value:
            raise APIException(ErrorCode.INVITATION_NOT_FOR_ME)

        if invitation.status != InvitationStatus.PENDING:
            raise APIException(ErrorCode.INVITATION_ALREADY_RESPONDED)

        # 백준 연동 재확인
        user_info = await self.user_search_repository.find_by_user_account_id(requester_id.value)
        if user_info is None:
            raise APIException(ErrorCode.BJ_ACCOUNT_NOT_LINKED)

        study = await self.study_repository.find_by_id(invitation.study_id)
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if study.is_full():
            raise APIException(ErrorCode.STUDY_FULL)

        invitation.accept()
        await self.invitation_repository.update(invitation)

        study.add_member(requester_id)
        await self.study_repository.update(study)

        # 방장에게 Notice (초대 수락)
        notice = Notice.create(
            recipient_user_account_id=study.owner_user_account_id,
            category=NoticeCategory.STUDY_INVITATION_STATUS,
            title="스터디 초대 수락",
            content={
                "studyName": study.study_name,
                "userId": user_info.bj_account_id,
                "userCode": user_info.user_code,
                "status": "ACCEPTED",
                "senderUserAccountId": requester_id.value,
            },
            reference_id=study.study_id.value,
            reference_type="STUDY",
        )
        await self.notice_repository.insert(notice)
        await self.notice_sse_manager.notify(
            study.owner_user_account_id.value,
            {"type": "STUDY_INVITATION_STATUS", "studyId": study.study_id.value},
        )
