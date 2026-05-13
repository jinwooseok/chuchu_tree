import logging

from app.common.domain.vo.identifiers import UserAccountId
from app.common.infra.event.decorators import event_register_handlers, event_handler
from app.core.database import transactional
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_problem_repository import StudyProblemRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.user.application.command.user_account_command import DeleteUserAccountCommand

logger = logging.getLogger(__name__)


@event_register_handlers()
class StudyWithdrawalService:
    def __init__(
        self,
        study_repository: StudyRepository,
        study_problem_repository: StudyProblemRepository,
        notice_repository: NoticeRepository,
        study_invitation_repository: StudyInvitationRepository,
        study_application_repository: StudyApplicationRepository,
    ):
        self.study_repository = study_repository
        self.study_problem_repository = study_problem_repository
        self.notice_repository = notice_repository
        self.study_invitation_repository = study_invitation_repository
        self.study_application_repository = study_application_repository

    @event_handler("USER_ACCOUNT_WITHDRAWAL_REQUESTED")
    @transactional
    async def delete_study_data(self, command: DeleteUserAccountCommand) -> bool:
        user_account_id = command.user_account_id
        uid = UserAccountId(user_account_id)

        # 1. notice Hard Delete (FK: recipient_user_account_id → user_account)
        await self.notice_repository.delete_all_by_user_account_id(uid)

        # 2. study_invitation Hard Delete (FK: invitee/inviter_user_account_id → user_account)
        await self.study_invitation_repository.delete_all_by_user_account_id(uid)

        # 3. study_application Hard Delete (FK: applicant_user_account_id → user_account)
        await self.study_application_repository.delete_all_by_user_account_id(uid)

        # 4. study_problem_member Hard Delete
        await self.study_problem_repository.delete_members_by_user_hard(user_account_id)

        # 5. 참여 중인 스터디에서 방장 위임 후 멤버 제거 (soft delete)
        studies = await self.study_repository.find_by_member_user_account_id(uid)
        for study in studies:
            if study.is_owner(uid):
                remaining = [
                    m for m in study.members
                    if m.deleted_at is None and m.user_account_id.value != user_account_id
                ]
                if not remaining:
                    await self.study_repository.soft_delete(study)
                    await self.study_application_repository.soft_delete_all_by_study_id(study.study_id)
                    continue
                study.delegate_owner(remaining[0].user_account_id.value)
            study.remove_member(uid)
            await self.study_repository.update(study)

        # 6. study_member Hard Delete (soft delete된 행 포함, FK: user_account_id → user_account)
        await self.study_repository.delete_members_by_user_hard(user_account_id)

        logger.info(f"[StudyWithdrawalService] 스터디 데이터 정리 완료: user_account_id={user_account_id}")
        return True
