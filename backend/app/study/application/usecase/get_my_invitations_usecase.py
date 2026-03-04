from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.study.application.command.study_command import GetMyInvitationsCommand
from app.study.application.query.invitation_query import InvitationQuery
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class GetMyInvitationsUsecase:
    def __init__(
        self,
        invitation_repository: StudyInvitationRepository,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
    ):
        self.invitation_repository = invitation_repository
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository

    @transactional(readonly=True)
    async def execute(self, command: GetMyInvitationsCommand) -> list[InvitationQuery]:
        invitee_id = UserAccountId(command.requester_user_account_id)
        invitations = await self.invitation_repository.find_pending_by_invitee(invitee_id)

        # bulk 조회
        inviter_ids = list({inv.inviter_user_account_id.value for inv in invitations})
        study_ids = list({inv.study_id.value for inv in invitations})

        inviter_map = {
            u.user_account_id: u
            for u in await self.user_search_repository.find_by_user_account_ids(inviter_ids)
        }

        result = []
        for inv in invitations:
            study = await self.study_repository.find_by_id(inv.study_id)
            inviter = inviter_map.get(inv.inviter_user_account_id.value)
            result.append(
                InvitationQuery(
                    invitation_id=inv.invitation_id.value,
                    study_id=inv.study_id.value,
                    study_name=study.study_name if study else "",
                    inviter_user_account_id=inv.inviter_user_account_id.value,
                    inviter_bj_account_id=inviter.bj_account_id if inviter else "",
                    inviter_user_code=inviter.user_code if inviter else "",
                    status=inv.status.value,
                    created_at=inv.created_at.isoformat(),
                )
            )
        return result
