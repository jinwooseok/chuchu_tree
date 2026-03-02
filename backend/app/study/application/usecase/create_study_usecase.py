from app.common.domain.enums import StudyMemberRole
from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import CreateStudyCommand
from app.study.application.query.study_query import CreateStudyQuery
from app.study.domain.entity.study import Study
from app.study.domain.entity.study_invitation import StudyInvitation
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class CreateStudyUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        invitation_repository: StudyInvitationRepository,
        user_search_repository: UserSearchRepository,
    ):
        self.study_repository = study_repository
        self.invitation_repository = invitation_repository
        self.user_search_repository = user_search_repository

    @transactional
    async def execute(self, command: CreateStudyCommand) -> CreateStudyQuery:
        # 1. 요청자 백준 연동 확인
        requester = await self.user_search_repository.find_by_user_account_id(command.requester_user_account_id)
        if requester is None:
            raise APIException(ErrorCode.BJ_ACCOUNT_NOT_LINKED)

        # 2. 스터디명 중복 확인
        if await self.study_repository.is_name_taken(command.study_name):
            raise APIException(ErrorCode.STUDY_NAME_ALREADY_TAKEN)

        # 3. invitee 백준 연동 확인
        for invitee_id in command.invitee_user_account_ids:
            invitee = await self.user_search_repository.find_by_user_account_id(invitee_id)
            if invitee is None:
                raise APIException(ErrorCode.BJ_ACCOUNT_NOT_LINKED)

        # 4. Study 생성
        owner_id = UserAccountId(command.requester_user_account_id)
        study = Study.create(
            study_name=command.study_name,
            owner_user_account_id=owner_id,
            description=command.description,
            max_members=command.max_members,
        )
        study.add_member(owner_id, StudyMemberRole.OWNER)

        # 5. 저장
        saved_study = await self.study_repository.insert(study)

        # 6. 초대장 발송
        for invitee_id in command.invitee_user_account_ids:
            invitation = StudyInvitation.create(
                study_id=saved_study.study_id,
                invitee_user_account_id=UserAccountId(invitee_id),
                inviter_user_account_id=owner_id,
            )
            await self.invitation_repository.insert(invitation)

        return CreateStudyQuery(
            study_id=saved_study.study_id.value,
            study_name=saved_study.study_name,
            owner_user_account_id=saved_study.owner_user_account_id.value,
            description=saved_study.description,
            max_members=saved_study.max_members,
            member_count=saved_study.active_member_count(),
            created_at=saved_study.created_at.isoformat(),
        )
