from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import NoticeCategory, NoticeCategoryDetail
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import ApplyToStudyCommand
from app.study.domain.entity.study_application import StudyApplication
from app.study.domain.event.payloads import NoticeRequestedPayload
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class ApplyToStudyUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        user_search_repository: UserSearchRepository,
        domain_event_bus: DomainEventBus,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.user_search_repository = user_search_repository
        self.domain_event_bus = domain_event_bus

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

        # owner에게 Notice 이벤트 발행
        await self.domain_event_bus.publish(
            DomainEvent(
                event_type="NOTICE_REQUESTED",
                data=NoticeRequestedPayload(
                    recipient_user_account_id=study.owner_user_account_id.value,
                    category=NoticeCategory.STUDY_APPLICATION.value,
                    category_detail=NoticeCategoryDetail.REQUESTED_STUDY_APPLICATION.value,
                    content={
                        "applicationId": saved.application_id.value,
                        "studyId": study.study_id.value,
                        "studyName": study.study_name,
                        "applicantUserAccountId": command.requester_user_account_id,
                        "applicantBjAccountId": user_info.bj_account_id,
                        "applicantUserCode": user_info.user_code,
                        "status": "PENDING",
                    },
                ),
            ),
            after_commit=True,
        )
