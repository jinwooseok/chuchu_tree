from datetime import date
from app.common.domain.enums import NoticeCategory
from app.common.domain.vo.identifiers import ProblemId, StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.application.command.study_command import AssignStudyProblemCommand
from app.study.domain.entity.notice import Notice
from app.study.domain.entity.study_problem import StudyProblem, StudyProblemMember
from app.study.domain.repository.notice_repository import NoticeRepository
from app.study.domain.repository.study_problem_repository import StudyProblemRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository
from app.study.infra.sse.notice_manager import NoticeSSEManager


class AssignStudyProblemUsecase:
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
    async def execute(self, command: AssignStudyProblemCommand) -> None:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_owner(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_OWNER_ONLY)

        active_member_ids = {m.user_account_id.value for m in study.members if m.deleted_at is None}
        for assignment in command.assignments:
            if assignment.user_account_id not in active_member_ids:
                raise APIException(ErrorCode.STUDY_PROBLEM_INVALID_TARGETS)

        study_problem = StudyProblem.create(
            study_id=study.study_id,
            problem_id=ProblemId(command.problem_id),
            assigned_by_user_account_id=UserAccountId(command.requester_user_account_id),
        )
        members = [
            StudyProblemMember.create(
                study_problem_id=None,
                user_account_id=UserAccountId(a.user_account_id),
                target_date=date.fromisoformat(a.target_date),
            )
            for a in command.assignments
        ]
        saved_problem = await self.study_problem_repository.insert(study_problem, members)

        target_user_ids = [a.user_account_id for a in command.assignments]
        # 각 멤버별 target_date를 매핑
        uid_to_dates: dict[int, list[str]] = {}
        for a in command.assignments:
            uid_to_dates.setdefault(a.user_account_id, []).append(a.target_date)

        notices = [
            Notice.create(
                recipient_user_account_id=UserAccountId(uid),
                category=NoticeCategory.STUDY_PROBLEMS_STATUS,
                title="새 풀문제 할당",
                content={
                    "studyName": study.study_name,
                    "calendarDate": uid_to_dates[uid][0],
                },
                reference_id=saved_problem.study_problem_id.value,
                reference_type="STUDY_PROBLEM",
            )
            for uid in set(target_user_ids)
        ]
        await self.notice_repository.insert_many(notices)
        for uid in set(target_user_ids):
            await self.notice_sse_manager.notify(
                uid,
                {"type": "STUDY_PROBLEMS_STATUS", "studyId": study.study_id.value},
            )
