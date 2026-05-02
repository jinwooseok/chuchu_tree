from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import ApplicationStatus, NoticeCategory, NoticeCategoryDetail
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import StudyApplicationId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import RejectStudyApplicationCommand
from app.study.domain.event.payloads import NoticeRequestedPayload
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class RejectStudyApplicationUsecase:
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

        # owner 정보 조회
        owner_info = await self.user_search_repository.find_by_user_account_id(
            study.owner_user_account_id.value
        )

        # 신청자에게 Notice 이벤트 발행 (거절)
        await self.domain_event_bus.publish(
            DomainEvent(
                event_type="NOTICE_REQUESTED",
                data=NoticeRequestedPayload(
                    recipient_user_account_id=application.applicant_user_account_id.value,
                    category=NoticeCategory.STUDY_APPLICATION.value,
                    category_detail=NoticeCategoryDetail.RESPONSED_STUDY_APPLICATION.value,
                    content={
                        "studyId": study.study_id.value,
                        "studyName": study.study_name,
                        "ownerUserAccountId": study.owner_user_account_id.value,
                        "ownerBjAccountId": owner_info.bj_account_id if owner_info else "",
                        "ownerUserCode": owner_info.user_code if owner_info else "",
                        "status": "REJECTED",
                    },
                ),
            ),
            after_commit=True,
        )
