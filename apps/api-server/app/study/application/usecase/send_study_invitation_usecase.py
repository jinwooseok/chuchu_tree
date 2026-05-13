from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import NoticeCategory, NoticeCategoryDetail
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import SendStudyInvitationCommand
from app.study.domain.entity.study_invitation import StudyInvitation
from app.study.domain.event.payloads import NoticeRequestedPayload
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class SendStudyInvitationUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        invitation_repository: StudyInvitationRepository,
        user_search_repository: UserSearchRepository,
        domain_event_bus: DomainEventBus,
    ):
        self.study_repository = study_repository
        self.invitation_repository = invitation_repository
        self.user_search_repository = user_search_repository
        self.domain_event_bus = domain_event_bus

    @transactional
    async def execute(self, command: SendStudyInvitationCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_owner(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_OWNER_ONLY)

        # invitee 백준 연동 확인
        invitee_info = await self.user_search_repository.find_by_user_account_id(command.invitee_user_account_id)
        if invitee_info is None:
            raise APIException(ErrorCode.BJ_ACCOUNT_NOT_LINKED)

        invitee_id = UserAccountId(command.invitee_user_account_id)
        if study.is_member(invitee_id):
            raise APIException(ErrorCode.STUDY_ALREADY_MEMBER)

        # 기존 초대 확인
        existing = await self.invitation_repository.find_by_study_and_invitee(
            StudyId(command.study_id), invitee_id
        )
        if existing is not None:
            raise APIException(ErrorCode.INVITATION_ALREADY_SENT)

        # inviter 정보 조회
        inviter_info = await self.user_search_repository.find_by_user_account_id(command.requester_user_account_id)
        inviter_bj_id = inviter_info.bj_account_id if inviter_info else ""
        inviter_user_code = inviter_info.user_code if inviter_info else ""

        invitation = StudyInvitation.create(
            study_id=study.study_id,
            invitee_user_account_id=invitee_id,
            inviter_user_account_id=UserAccountId(command.requester_user_account_id),
        )
        saved = await self.invitation_repository.insert(invitation)

        # invitee에게 Notice 이벤트 발행
        await self.domain_event_bus.publish(
            DomainEvent(
                event_type="NOTICE_REQUESTED",
                data=NoticeRequestedPayload(
                    recipient_user_account_id=command.invitee_user_account_id,
                    category=NoticeCategory.STUDY_INVITATION.value,
                    category_detail=NoticeCategoryDetail.REQUESTED_STUDY_INVITATION.value,
                    content={
                        "invitationId": saved.invitation_id.value,
                        "studyId": study.study_id.value,
                        "studyName": study.study_name,
                        "inviterUserAccountId": command.requester_user_account_id,
                        "inviterBjAccountId": inviter_bj_id,
                        "inviterUserCode": inviter_user_code,
                        "status": "PENDING",
                    },
                ),
            ),
            after_commit=True,
        )
