from app.common.domain.enums import NoticeCategory
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import ApplyToStudyCommand
from app.study.domain.entity.notice import Notice
from app.study.domain.entity.study_application import StudyApplication
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.study.infra.sse.notice_manager import NoticeSSEManager


class ApplyToStudyUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        user_search_repository: UserSearchRepository,
        notice_repository: NoticeRepository,
        notice_sse_manager: NoticeSSEManager,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.user_search_repository = user_search_repository
        self.notice_repository = notice_repository
        self.notice_sse_manager = notice_sse_manager

    @transactional
    async def execute(self, command: ApplyToStudyCommand) -> None:
        # 백준 연동 확인
        user_info = await self.user_search_repository.find_by_user_account_id(command.requester_user_account_id)
        if user_info is None:
            raise APIException(ErrorCode.BJ_ACCOUNT_NOT_LINKED)

        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)

        applicant_id = UserAccountId(command.requester_user_account_id)
        if study.is_member(applicant_id):
            raise APIException(ErrorCode.STUDY_ALREADY_MEMBER)

        existing = await self.application_repository.find_by_study_and_applicant(
            study.study_id, applicant_id
        )
        if existing is not None:
            raise APIException(ErrorCode.APPLICATION_ALREADY_SENT)

        application = StudyApplication.create(
            study_id=study.study_id,
            applicant_user_account_id=applicant_id,
            message=command.message,
        )
        saved = await self.application_repository.insert(application)

        # owner에게 Notice + SSE
        owner_id = study.owner_user_account_id.value
        notice = Notice.create(
            recipient_user_account_id=study.owner_user_account_id,
            category=NoticeCategory.STUDY_APPLICATION_STATUS,
            title="스터디 가입 신청",
            content={
                "studyName": study.study_name,
                "status": "PENDING",
            },
            reference_id=saved.application_id.value,
            reference_type="STUDY_APPLICATION",
        )
        await self.notice_repository.insert(notice)
        await self.notice_sse_manager.notify(
            owner_id,
            {"type": "STUDY_APPLICATION_STATUS", "studyId": study.study_id.value},
        )
