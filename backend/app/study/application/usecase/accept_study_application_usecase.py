from app.common.domain.enums import ApplicationStatus, InvitationStatus, NoticeCategory
from app.common.domain.vo.identifiers import StudyApplicationId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import AcceptStudyApplicationCommand
from app.study.domain.entity.notice import Notice
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.study.infra.sse.notice_manager import NoticeSSEManager


class AcceptStudyApplicationUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        invitation_repository: StudyInvitationRepository,
        user_search_repository: UserSearchRepository,
        notice_repository: NoticeRepository,
        notice_sse_manager: NoticeSSEManager,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.invitation_repository = invitation_repository
        self.user_search_repository = user_search_repository
        self.notice_repository = notice_repository
        self.notice_sse_manager = notice_sse_manager

    @transactional
    async def execute(self, command: AcceptStudyApplicationCommand) -> None:
        application = await self.application_repository.find_by_id(
            StudyApplicationId(command.application_id)
        )
        if application is None:
            raise APIException(ErrorCode.APPLICATION_NOT_FOUND)
        if application.status != ApplicationStatus.PENDING:
            raise APIException(ErrorCode.APPLICATION_ALREADY_RESPONDED)

        study = await self.study_repository.find_by_id(application.study_id)
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_owner(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_OWNER_ONLY)

        applicant_info = await self.user_search_repository.find_by_user_account_id(
            application.applicant_user_account_id.value
        )
        if applicant_info is None:
            raise APIException(ErrorCode.BJ_ACCOUNT_NOT_LINKED)

        if study.is_full():
            raise APIException(ErrorCode.STUDY_FULL)

        application.accept()
        await self.application_repository.update(application)

        study.add_member(application.applicant_user_account_id)
        await self.study_repository.update(study)

        # 동일 스터디에 PENDING 초대가 있으면 정리
        pending_invitation = await self.invitation_repository.find_by_study_and_invitee(
            application.study_id, application.applicant_user_account_id
        )
        if pending_invitation is not None and pending_invitation.status == InvitationStatus.PENDING:
            await self.invitation_repository.soft_delete(pending_invitation)

        # 신청자에게 Notice (수락)
        notice = Notice.create(
            recipient_user_account_id=application.applicant_user_account_id,
            category=NoticeCategory.STUDY_APPLICATION_STATUS,
            title="가입 신청 수락",
            content={
                "studyName": study.study_name,
                "status": "ACCEPTED",
            },
            reference_id=study.study_id.value,
            reference_type="STUDY",
        )
        await self.notice_repository.insert(notice)
        await self.notice_sse_manager.notify(
            application.applicant_user_account_id.value,
            {"type": "STUDY_APPLICATION_STATUS", "studyId": study.study_id.value, "accepted": True},
        )
