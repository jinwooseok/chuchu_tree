from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.common.domain.enums import ExclusionMode
from app.common.domain.vo.identifiers import BaekjoonAccountId, StudyId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.recommendation.application.usecase.recommend_problems_usecase import RecommendProblemsUsecase
from app.study.application.command.study_command import RecommendStudyProblemsCommand
from app.study.application.query.study_recommend_query import (
    StudyMemberSolveInfoQuery,
    StudyRecommendedProblemQuery,
    StudyRecommendProblemsQuery,
)
from app.study.domain.repository.study_repository import StudyRepository
from app.study.domain.repository.user_search_repository import UserSearchRepository


class RecommendStudyProblemsUsecase:
    def __init__(
        self,
        study_repository: StudyRepository,
        user_search_repository: UserSearchRepository,
        problem_history_repository: ProblemHistoryRepository,
        recommend_problems_usecase: RecommendProblemsUsecase,
    ):
        self.study_repository = study_repository
        self.user_search_repository = user_search_repository
        self.problem_history_repository = problem_history_repository
        self.recommend_problems_usecase = recommend_problems_usecase

    @transactional(readonly=True)
    async def execute(self, command: RecommendStudyProblemsCommand) -> StudyRecommendProblemsQuery:
        study = await self.study_repository.find_by_id(StudyId(command.study_id))
        if study is None:
            raise APIException(ErrorCode.STUDY_NOT_FOUND)
        if not study.is_member(UserAccountId(command.requester_user_account_id)):
            raise APIException(ErrorCode.STUDY_NOT_MEMBER)

        target_user_account_id = command.target_user_account_id or command.requester_user_account_id

        # BJ 계정 연동된 스터디 활성 멤버만 조회 (INNER JOIN으로 연동 멤버만 반환)
        active_member_ids = [m.user_account_id.value for m in study.members if m.deleted_at is None]
        user_infos = await self.user_search_repository.find_by_user_account_ids(active_member_ids)
        user_map = {u.user_account_id: u for u in user_infos}

        # bj_account_id → 풀이한 problem_id set 조회
        solved_map: dict[str, set[int]] = {}
        for u in user_infos:
            solved_ids = await self.problem_history_repository.find_solved_ids_by_bj_account_id(
                BaekjoonAccountId(u.bj_account_id)
            )
            solved_map[u.bj_account_id] = set(solved_ids)

        exclusion_mode = command.exclusion_mode if isinstance(command.exclusion_mode, ExclusionMode) else ExclusionMode(command.exclusion_mode)

        # recommend_all_unsolved: 스터디 멤버 중 한 명이라도 푼 문제 ID를 미리 계산하여 추천 도메인에 전달
        additional_excluded: set[int] | None = None
        if command.recommend_all_unsolved:
            any_member_solved: set[int] = set()
            for s_ids in solved_map.values():
                any_member_solved |= s_ids
            additional_excluded = any_member_solved if any_member_solved else None

        # 추천 실행 (중첩 트랜잭션 - savepoint)
        recommend_query = await self.recommend_problems_usecase.execute(
            user_account_id=UserAccountId(target_user_account_id),
            level_filter_codes=command.level_filter_codes,
            tag_filter_codes=command.tag_filter_codes,
            count=command.count,
            exclusion_mode=exclusion_mode,
            additional_excluded_problem_ids=additional_excluded,
            study_id=command.study_id,
            target_user_account_id=command.target_user_account_id,
            recommend_all_unsolved=command.recommend_all_unsolved,
        )

        # studyMemberSolveInfo 조립 (solved_map은 이미 계산됨)
        result_problems = [
            StudyRecommendedProblemQuery(
                problem_id=problem_query.problem_id,
                problem_title=problem_query.problem_title,
                problem_tier_level=problem_query.problem_tier_level,
                problem_tier_name=problem_query.problem_tier_name,
                problem_class_level=problem_query.problem_class_level,
                recommend_reasons=problem_query.recommend_reasons,
                tags=problem_query.tags,
                study_member_solve_info=[
                    StudyMemberSolveInfoQuery(
                        user_account_id=uid,
                        bj_account_id=user_map[uid].bj_account_id,
                        solved=problem_query.problem_id in solved_map.get(user_map[uid].bj_account_id, set()),
                    )
                    for uid in active_member_ids
                    if uid in user_map
                ],
            )
            for problem_query in recommend_query.problems
        ]

        return StudyRecommendProblemsQuery(problems=result_problems)
