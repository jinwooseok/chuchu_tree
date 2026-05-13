from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import InvitationStatus, NoticeCategory, NoticeCategoryDetail
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import StudyInvitationId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import AcceptStudyInvitationCommand
from app.study.domain.event.payloads import NoticeRequestedPayload
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class AcceptStudyInvitationUsecase:
    def __init__(
        self,
        invitation_repository: StudyInvitationRepository,
        study_repository: StudyRepository,
        application_repository: StudyApplicationRepository,
        user_search_repository: UserSearchRepository,
        domain_event_bus: DomainEventBus,
    ):
        self.invitation_repository = invitation_repository
        self.study_repository = study_repository
        self.application_repository = application_repository
        self.user_search_repository = user_search_repository
        self.domain_event_bus = domain_event_bus

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

        # 동일 스터디에 PENDING 신청이 있으면 정리
        pending_application = await self.application_repository.find_by_study_and_applicant(
            invitation.study_id, requester_id
        )
        if pending_application is not None:
            await self.application_repository.soft_delete(pending_application)

        # 방장에게 Notice 이벤트 발행 (초대 수락)
        await self.domain_event_bus.publish(
            DomainEvent(
                event_type="NOTICE_REQUESTED",
                data=NoticeRequestedPayload(
                    recipient_user_account_id=study.owner_user_account_id.value,
                    category=NoticeCategory.STUDY_INVITATION.value,
                    category_detail=NoticeCategoryDetail.RESPONSED_STUDY_INVITATION.value,
                    content={
                        "studyId": study.study_id.value,
                        "studyName": study.study_name,
                        "inviteeUserAccountId": requester_id.value,
                        "inviteeBjAccountId": user_info.bj_account_id,
                        "inviteeUserCode": user_info.user_code,
                        "status": "ACCEPTED",
                    },
                ),
            ),
            after_commit=True,
        )
