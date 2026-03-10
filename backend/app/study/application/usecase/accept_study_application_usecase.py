from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import ApplicationStatus, InvitationStatus, NoticeCategory, NoticeCategoryDetail
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import StudyApplicationId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import AcceptStudyApplicationCommand
from app.study.domain.event.payloads import NoticeRequestedPayload
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class AcceptStudyApplicationUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        invitation_repository: StudyInvitationRepository,
        user_search_repository: UserSearchRepository,
        domain_event_bus: DomainEventBus,
    ):
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.invitation_repository = invitation_repository
        self.user_search_repository = user_search_repository
        self.domain_event_bus = domain_event_bus

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

        # owner 정보 조회
        owner_info = await self.user_search_repository.find_by_user_account_id(
            study.owner_user_account_id.value
        )

        # 신청자에게 Notice 이벤트 발행 (수락)
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
                        "status": "ACCEPTED",
                    },
                    reference_id=study.study_id.value,
                    reference_type="STUDY",
                ),
            ),
            after_commit=True,
        )
