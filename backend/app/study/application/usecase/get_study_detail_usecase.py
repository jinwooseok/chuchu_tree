from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import GetStudyDetailCommand
from app.study.application.query.study_query import (
    StudyDetailQuery,
    StudyMemberQuery,
    StudyPendingApplicationQuery,
    StudyPendingInvitationQuery,
)
from app.study.domain.repository.study_application_repository import StudyApplicationRepository
from app.study.domain.repository.study_invitation_repository import StudyInvitationRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class GetStudyDetailUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
        invitation_repository: StudyInvitationRepository,
        application_repository: StudyApplicationRepository,
    ):
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository
        self.invitation_repository = invitation_repository
        self.application_repository = application_repository

    @transactional(readonly=True)
    async def execute(self, command: GetStudyDetailCommand) -> StudyDetailQuery:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)

        active_members = [m for m in study.members if m.deleted_at is None]
        member_ids = [m.user_account_id.value for m in active_members]
        user_infos = await self.user_search_repository.find_by_user_account_ids(member_ids)
        user_info_map = {u.user_account_id: u for u in user_infos}

        member_queries = []
        for member in active_members:
            info = user_info_map.get(member.user_account_id.value)
            member_queries.append(
                StudyMemberQuery(
                    user_account_id=member.user_account_id.value,
                    bj_account_id=info.bj_account_id if info else "",
                    user_code=info.user_code if info else "",
                    role=member.role.value,
                    joined_at=member.joined_at.isoformat(),
                )
            )

        # 대기 중인 초대 목록
        invitations = await self.invitation_repository.find_pending_by_study(StudyId(command.study_id))
        invitee_ids = list({inv.invitee_user_account_id.value for inv in invitations})
        invitee_infos = await self.user_search_repository.find_by_user_account_ids(invitee_ids)
        invitee_map = {u.user_account_id: u for u in invitee_infos}
        pending_invitations = [
            StudyPendingInvitationQuery(
                invitation_id=inv.invitation_id.value,
                invitee_user_account_id=inv.invitee_user_account_id.value,
                invitee_bj_account_id=invitee_map[inv.invitee_user_account_id.value].bj_account_id
                if inv.invitee_user_account_id.value in invitee_map else "",
                invitee_user_code=invitee_map[inv.invitee_user_account_id.value].user_code
                if inv.invitee_user_account_id.value in invitee_map else "",
                created_at=inv.created_at.isoformat(),
            )
            for inv in invitations
        ]

        # 대기 중인 신청 목록
        applications = await self.application_repository.find_pending_by_study(StudyId(command.study_id))
        applicant_ids = list({app.applicant_user_account_id.value for app in applications})
        applicant_infos = await self.user_search_repository.find_by_user_account_ids(applicant_ids)
        applicant_map = {u.user_account_id: u for u in applicant_infos}
        pending_applications = [
            StudyPendingApplicationQuery(
                application_id=app.application_id.value,
                applicant_user_account_id=app.applicant_user_account_id.value,
                applicant_bj_account_id=applicant_map[app.applicant_user_account_id.value].bj_account_id
                if app.applicant_user_account_id.value in applicant_map else "",
                applicant_user_code=applicant_map[app.applicant_user_account_id.value].user_code
                if app.applicant_user_account_id.value in applicant_map else "",
                created_at=app.created_at.isoformat(),
            )
            for app in applications
        ]

        return StudyDetailQuery(
            study_id=study.study_id.value,
            study_name=study.study_name,
            owner_user_account_id=study.owner_user_account_id.value,
            description=study.description,
            max_members=study.max_members,
            member_count=len(active_members),
            created_at=study.created_at.isoformat(),
            members=member_queries,
            pending_invitations=pending_invitations,
            pending_applications=pending_applications,
        )
