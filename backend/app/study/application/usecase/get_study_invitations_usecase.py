from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import GetStudyInvitationsCommand
from app.study.application.query.invitation_query import InvitationQuery
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class GetStudyInvitationsUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        invitation_repository: StudyInvitationRepository,
        user_search_repository: UserSearchRepository,
    ):
        self.study_repository = study_repository
        self.invitation_repository = invitation_repository
        self.user_search_repository = user_search_repository

    @transactional(readonly=True)
    async def execute(self, command: GetStudyInvitationsCommand) -> list[InvitationQuery]:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        invitations = await self.invitation_repository.find_pending_by_study(StudyId(command.study_id))

        invitee_ids = list({inv.invitee_user_account_id.value for inv in invitations})
        invitee_map = {
            u.user_account_id: u
            for u in await self.user_search_repository.find_by_user_account_ids(invitee_ids)
        }

        return [
            InvitationQuery(
                invitation_id=inv.invitation_id.value,
                study_id=inv.study_id.value,
                study_name=study.study_name,
                inviter_user_account_id=inv.inviter_user_account_id.value,
                inviter_bj_account_id=invitee_map[inv.invitee_user_account_id.value].bj_account_id
                if inv.invitee_user_account_id.value in invitee_map else "",
                inviter_user_code=invitee_map[inv.invitee_user_account_id.value].user_code
                if inv.invitee_user_account_id.value in invitee_map else "",
                status=inv.status.value,
                created_at=inv.created_at.isoformat(),
            )
            for inv in invitations
        ]
