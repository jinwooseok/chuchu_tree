from datetime import date
from app.common.domain.enums import NoticeCategory
from app.common.domain.vo.identifiers import ProblemId, StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import AssignStudyProblemAllCommand
from app.study.domain.entity.notice import Notice
from app.study.domain.entity.study_problem import StudyProblem, StudyProblemMember
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.study_problem_repository import StudyProblemRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.study.infra.sse.notice_manager import NoticeSSEManager


class AssignStudyProblemAllUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        study_problem_repository: StudyProblemRepository,
        user_search_repository: UserSearchRepository,
        notice_repository: NoticeRepository,
        notice_sse_manager: NoticeSSEManager,
    ):
        self.study_repository = study_repository
        self.study_problem_repository = study_problem_repository
        self.user_search_repository = user_search_repository
        self.notice_repository = notice_repository
        self.notice_sse_manager = notice_sse_manager

    @transactional
    async def execute(self, command: AssignStudyProblemAllCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        active_member_ids = [m.user_account_id.value for m in study.members if m.deleted_at is None]
        linked_users = await self.user_search_repository.find_by_user_account_ids(active_member_ids)
        linked_ids = [u.user_account_id for u in linked_users]

        target_date = date.fromisoformat(command.target_date)
        study_problem = StudyProblem.create(
            study_id=study.study_id,
            problem_id=ProblemId(command.problem_id),
            assigned_by_user_account_id=UserAccountId(command.requester_user_account_id),
        )
        members = [
            StudyProblemMember.create(
                study_problem_id=None,
                user_account_id=UserAccountId(uid),
                target_date=target_date,
            )
            for uid in linked_ids
        ]
        saved_problem = await self.study_problem_repository.insert(study_problem, members)

        # 연동된 멤버 전원에게 Notice
        notices = [
            Notice.create(
                recipient_user_account_id=UserAccountId(uid),
                category=NoticeCategory.STUDY_PROBLEMS_STATUS,
                title="새 풀문제 할당",
                content={
                    "studyName": study.study_name,
                    "calendarDate": target_date.isoformat(),
                },
                reference_id=saved_problem.study_problem_id.value,
                reference_type="STUDY_PROBLEM",
            )
            for uid in linked_ids
        ]
        await self.notice_repository.insert_many(notices)
        for uid in linked_ids:
            await self.notice_sse_manager.notify(
                uid,
                {"type": "STUDY_PROBLEMS_STATUS", "studyId": study.study_id.value},
            )
