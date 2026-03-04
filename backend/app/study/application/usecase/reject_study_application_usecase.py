from app.common.domain.enums import ApplicationStatus, NoticeCategory
from app.common.domain.vo.identifiers import StudyApplicationId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import RejectStudyApplicationCommand
from app.study.domain.entity.notice import Notice
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.infra.sse.notice_manager import NoticeSSEManager


class RejectStudyApplicationUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        notice_repository: NoticeRepository,
        notice_sse_manager: NoticeSSEManager,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.notice_repository = notice_repository
        self.notice_sse_manager = notice_sse_manager

    @transactional
    async def execute(self, command: RejectStudyApplicationCommand) -> None:
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

        application.reject()
        await self.application_repository.update(application)

        # 신청자에게 Notice (거절)
        notice = Notice.create(
            recipient_user_account_id=application.applicant_user_account_id,
            category=NoticeCategory.STUDY_APPLICATION_STATUS,
            title="가입 신청 거절",
            content={
                "studyName": study.study_name,
                "status": "REJECTED",
            },
            reference_id=study.study_id.value,
            reference_type="STUDY",
        )
        await self.notice_repository.insert(notice)
        await self.notice_sse_manager.notify(
            application.applicant_user_account_id.value,
            {"type": "STUDY_APPLICATION_STATUS", "studyId": study.study_id.value, "accepted": False},
        )
