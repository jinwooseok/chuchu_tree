import logging

from app.common.domain.vo.identifiers import UserAccountId
from app.common.infra.event.decorators import event_register_handlers, event_handler
from app.core.database import transactional
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
    ):
        self.study_repository = study_repository
        self.study_problem_repository = study_problem_repository

    @event_handler("USER_ACCOUNT_WITHDRAWAL_REQUESTED")
    @transactional
    async def delete_study_data(self, command: DeleteUserAccountCommand) -> bool:
        user_account_id = command.user_account_id

        # 1. study_problem_member Hard Delete
        await self.study_problem_repository.delete_members_by_user_hard(user_account_id)

        # 2. 참여 중인 스터디에서 방장 위임 후 멤버 제거
        studies = await self.study_repository.find_by_member_user_account_id(
            UserAccountId(user_account_id)
        )
        uid = UserAccountId(user_account_id)
        for study in studies:
            if study.is_owner(uid):
                remaining = [
                    m for m in study.members
                    if m.deleted_at is None and m.user_account_id.value != user_account_id
                ]
                if not remaining:
                    await self.study_repository.soft_delete(study)
                    continue
                study.delegate_owner(remaining[0].user_account_id.value)
            study.remove_member(uid)
            await self.study_repository.update(study)

        logger.info(f"[StudyWithdrawalService] 스터디 데이터 정리 완료: user_account_id={user_account_id}")
        return True
