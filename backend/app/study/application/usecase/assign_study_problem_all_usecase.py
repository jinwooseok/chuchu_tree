from datetime import date
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import NoticeCategory, NoticeCategoryDetail
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import ProblemId, StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.study.application.command.study_command import AssignStudyProblemAllCommand
from app.study.domain.entity.study_problem import StudyProblem, StudyProblemMember
from app.study.domain.event.payloads import NoticeRequestedPayload
from app.study.domain.repository.study_problem_repository import StudyProblemRepository
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class AssignStudyProblemAllUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        study_problem_repository: StudyProblemRepository,
        user_search_repository: UserSearchRepository,
        problem_repository: ProblemRepository,
        domain_event_bus: DomainEventBus,
    ):
        self.study_repository = study_repository
        self.study_problem_repository = study_problem_repository
        self.user_search_repository = user_search_repository
        self.problem_repository = problem_repository
        self.domain_event_bus = domain_event_bus

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
        linked_user_map = {u.user_account_id: u for u in linked_users}

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

        # assigner 정보 조회
        assigner_info = await self.user_search_repository.find_by_user_account_id(command.requester_user_account_id)
        assigner_bj_id = assigner_info.bj_account_id if assigner_info else ""
        assigner_user_code = assigner_info.user_code if assigner_info else ""

        # problem title 조회
        problem = await self.problem_repository.find_by_id(ProblemId(command.problem_id))
        problem_title = problem.title if problem else ""

        assigner_id = command.requester_user_account_id

        for uid in linked_ids:
            # 수신자는 assigner 제외
            if uid == assigner_id:
                continue

            # assignees: 수신자 본인 제외
            assignees_for_recipient = [
                {
                    "userAccountId": other_uid,
                    "bjAccountId": linked_user_map[other_uid].bj_account_id if other_uid in linked_user_map else "",
                    "userCode": linked_user_map[other_uid].user_code if other_uid in linked_user_map else "",
                }
                for other_uid in linked_ids
            ]

            await self.domain_event_bus.publish(
                DomainEvent(
                    event_type="NOTICE_REQUESTED",
                    data=NoticeRequestedPayload(
                        recipient_user_account_id=uid,
                        category=NoticeCategory.STUDY_PROBLEM.value,
                        category_detail=NoticeCategoryDetail.ASSIGNED_STUDY_PROBLEM.value,
                        content={
                            "studyProblemId": saved_problem.study_problem_id.value,
                            "studyId": study.study_id.value,
                            "studyName": study.study_name,
                            "assignerUserAccountId": assigner_id,
                            "assignerBjAccountId": assigner_bj_id,
                            "assignerUserCode": assigner_user_code,
                            "assignees": assignees_for_recipient,
                            "problemId": command.problem_id,
                            "problemTitle": problem_title,
                            "calendarDate": target_date.isoformat(),
                        },
                    ),
                ),
                after_commit=True,
            )
