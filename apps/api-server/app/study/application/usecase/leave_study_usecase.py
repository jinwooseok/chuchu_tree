from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import LeaveStudyCommand
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository


class LeaveStudyUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        invitation_repository: StudyInvitationRepository,
        application_repository: StudyApplicationRepository,
    ):
        self.study_repository = study_repository
        self.invitation_repository = invitation_repository
        self.application_repository = application_repository

    @transactional
    async def execute(self, command: LeaveStudyCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        requester_id = UserAccountId(command.requester_user_account_id)
        if not study.is_member(requester_id):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        if study.is_owner(requester_id):
            remaining = [
                m for m in study.members
                if m.deleted_at is None and m.user_account_id.value != command.requester_user_account_id
            ]
            if not remaining:
                # 마지막 멤버 → 스터디 soft delete + 초대/신청 정리
                await self.study_repository.soft_delete(study)
                await self.invitation_repository.soft_delete_all_by_study_id(StudyId(command.study_id))
                await self.application_repository.soft_delete_all_by_study_id(StudyId(command.study_id))
                return
            study.delegate_owner(remaining[0].user_account_id.value)

        study.remove_member(requester_id)
        await self.study_repository.update(study)
