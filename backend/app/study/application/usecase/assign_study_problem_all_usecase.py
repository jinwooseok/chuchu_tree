from datetime import date
from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.enums import NoticeCategory, NoticeCategoryDetail
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import ProblemId, StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.problem.application.query.problems_info_query import ProblemsInfoQuery
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.study.application.command.study_command import AssignStudyProblemAllCommand
from app.study.domain.entity.study_problem import StudyProblem, StudyProblemMember
from app.study.domain.event.payloads import NoticeRequestedPayload, StudyProblemAssignedPayload
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
        members = [
            StudyProblemMember.create(
                study_problem_id=None,
                user_account_id=UserAccountId(uid),
                target_date=target_date,
            )
            for uid in linked_ids
        ]

        # 같은 날짜에 이미 존재하는 StudyProblem 확인 (dedup)
        existing = await self.study_problem_repository.find_by_study_problem_and_date(
            StudyId(command.study_id), ProblemId(command.problem_id), target_date
        )
        if existing:
            saved_problem = await self.study_problem_repository.insert_members(existing, members)
        else:
            study_problem = StudyProblem.create(
                study_id=study.study_id,
                problem_id=ProblemId(command.problem_id),
                assigned_by_user_account_id=UserAccountId(command.requester_user_account_id),
            )
            saved_problem = await self.study_problem_repository.insert(study_problem, members)

        # assigner 정보 조회
        assigner_info = await self.user_search_repository.find_by_user_account_id(command.requester_user_account_id)
        assigner_bj_id = assigner_info.bj_account_id if assigner_info else ""
        assigner_user_code = assigner_info.user_code if assigner_info else ""

        # 문제 정보 조회 (tier, tags 포함)
        problems_info = await self._fetch_problem_info(command.problem_id)
        problem_info = problems_info.problems.get(command.problem_id)
        problem_title = problem_info.problem_title if problem_info else ""
        problem_tier_level = problem_info.problem_tier_level if problem_info else 0
        problem_tier_name = problem_info.problem_tier_name if problem_info else ""
        problem_class_level = problem_info.problem_class_level if problem_info else None
        tags = [t.model_dump() for t in problem_info.tags] if problem_info else []

        assigner_id = command.requester_user_account_id

        assignees_all = [
            {
                "userAccountId": uid,
                "bjAccountId": linked_user_map[uid].bj_account_id if uid in linked_user_map else "",
                "userCode": linked_user_map[uid].user_code if uid in linked_user_map else "",
            }
            for uid in linked_ids
        ]

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

        # Study SSE 이벤트 발행 (할당자 제외 스터디 전원 수신)
        await self.domain_event_bus.publish(
            DomainEvent(
                event_type="STUDY_PROBLEM_ASSIGNED",
                data=StudyProblemAssignedPayload(
                    study_id=study.study_id.value,
                    target_date=target_date.isoformat(),
                    study_problem_id=saved_problem.study_problem_id.value,
                    problem_id=command.problem_id,
                    problem_title=problem_title,
                    problem_tier_level=problem_tier_level,
                    problem_tier_name=problem_tier_name,
                    problem_class_level=problem_class_level,
                    tags=tags,
                    representative_tag=None,
                    assignees=assignees_all,
                    assigner_user_account_id=assigner_id,
                ),
            ),
            after_commit=True,
        )

    async def _fetch_problem_info(self, problem_id: int) -> ProblemsInfoQuery:
        event = DomainEvent(
            event_type="GET_PROBLEM_INFOS_REQUESTED",
            data=GetProblemsInfoPayload(problem_ids=[problem_id]),
            result_type=ProblemsInfoQuery,
        )
        return await self.domain_event_bus.publish(event)
