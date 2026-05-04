"""태그 별 푼 문제 조회 Usecase"""

import logging

from app.activity.domain.entity.problem_date_record import RecordType
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.common.domain.vo.identifiers import ProblemId, UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.problem.application.query.problems_info_query import TagAliasQuery, TagInfoQuery, TagTargetQuery
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.tag.domain.repository.tag_repository import TagRepository
from app.target.domain.repository.target_repository import TargetRepository
from app.tier.domain.repository.tier_repository import TierRepository
from app.user.application.command.get_tag_problems_command import GetTagProblemsCommand
from app.user.application.query.tag_problems_query import TagProblemQuery, TagProblemsQuery

logger = logging.getLogger(__name__)


class GetTagProblemsUsecase:
    """태그 별 푼 문제 조회 Usecase"""

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        tag_repository: TagRepository,
        problem_repository: ProblemRepository,
        user_activity_repository: UserActivityRepository,
        tier_repository: TierRepository,
        target_repository: TargetRepository,
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.tag_repository = tag_repository
        self.problem_repository = problem_repository
        self.user_activity_repository = user_activity_repository
        self.tier_repository = tier_repository
        self.target_repository = target_repository

    @transactional(readonly=True)
    async def execute(self, command: GetTagProblemsCommand) -> TagProblemsQuery:
        """
        태그 별 푼 문제 조회

        Args:
            command: 태그 별 푼 문제 조회 커맨드

        Returns:
            TagProblemsQuery: 해당 태그의 유저 푼 문제 목록
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 1. 백준 계정 조회
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)
        if not bj_account:
            logger.error(f"[GetTagProblemsUsecase] 백준 계정 연동 정보를 찾을 수 없음: {command.user_account_id}")
            raise APIException(ErrorCode.UNLINKED_USER)

        # 2. 태그 조회
        tag = await self.tag_repository.find_by_code(command.tag_code)
        if not tag:
            logger.error(f"[GetTagProblemsUsecase] 태그를 찾을 수 없음: {command.tag_code}")
            raise APIException(ErrorCode.TAG_NOT_FOUND)

        # 3. 해당 태그의 문제 ID 목록 조회
        problem_ids = await self.problem_repository.find_ids_by_tag_id(tag.tag_id)
        if not problem_ids:
            return TagProblemsQuery(total_problem_count=0, problems=[])

        # 4. 유저의 solved 상태 조회 (date_record 유무 무관하게 solved_yn=True 기준)
        solved_statuses = await self.user_activity_repository.find_solved_statuses_by_problem_ids(
            user_account_id, problem_ids
        )
        if not solved_statuses:
            return TagProblemsQuery(total_problem_count=0, problems=[])

        # 5. 문제별 가장 이른 solved 날짜 추출 (date_record 없으면 null)
        solved_problem_ids: list[int] = []
        solved_date_map: dict[int, str | None] = {}
        for status in solved_statuses:
            pid = status.problem_id.value
            solved_problem_ids.append(pid)
            dates = [
                dr.marked_date for dr in status.date_records
                if dr.record_type == RecordType.SOLVED and dr.deleted_at is None
            ]
            earliest_date = min(dates) if dates else None
            solved_date_map[pid] = earliest_date.isoformat() if earliest_date else None

        # 6. 문제 상세 조회 (태그 포함)
        p_ids = [ProblemId(pid) for pid in solved_problem_ids]
        problems = await self.problem_repository.find_by_ids(p_ids)
        if not problems:
            return TagProblemsQuery(total_problem_count=0, problems=[])

        # 7. tier_map, tag_map, tag_targets_map 구성
        unique_tier_levels = list({p.tier_level.value for p in problems})
        tiers = await self.tier_repository.find_by_levels(unique_tier_levels) if unique_tier_levels else []
        tier_map: dict[int, str] = {t.tier_level: t.tier_code for t in tiers}

        tag_ids_set = {pt.tag_id for p in problems for pt in p.tags}
        tag_entities = await self.tag_repository.find_by_ids_and_active(list(tag_ids_set)) if tag_ids_set else []
        tag_map = {t.tag_id.value: t for t in tag_entities}

        all_targets = await self.target_repository.find_all_active()
        tag_targets_map: dict[int, list] = {}
        for target in all_targets:
            for target_tag in target.required_tags:
                tid = target_tag.tag_id.value
                if tid not in tag_targets_map:
                    tag_targets_map[tid] = []
                tag_targets_map[tid].append(target)

        # 8. TagProblemQuery 조립
        tag_problem_queries: list[TagProblemQuery] = []
        for problem in problems:
            pid = problem.problem_id.value

            tag_queries: list[TagInfoQuery] = []
            for problem_tag in problem.tags:
                t = tag_map.get(problem_tag.tag_id.value)
                if not t:
                    continue
                tag_aliases = [TagAliasQuery(alias=a['alias']) for a in t.aliases]
                tag_targets = [
                    TagTargetQuery(
                        target_id=tgt.target_id.value,
                        target_code=tgt.code,
                        target_display_name=tgt.display_name,
                    )
                    for tgt in tag_targets_map.get(t.tag_id.value, [])
                ]
                tag_queries.append(TagInfoQuery(
                    tag_id=t.tag_id.value,
                    tag_code=t.code,
                    tag_display_name=t.tag_display_name,
                    tag_aliases=tag_aliases,
                    tag_targets=tag_targets,
                ))

            tag_problem_queries.append(TagProblemQuery(
                problem_id=pid,
                problem_title=problem.title,
                problem_tier_level=problem.tier_level.value,
                problem_tier_name=tier_map.get(problem.tier_level.value, "Unknown"),
                problem_class_level=problem.class_level,
                tags=tag_queries,
                solved_date=solved_date_map.get(pid),
            ))

        return TagProblemsQuery(
            total_problem_count=len(tag_problem_queries),
            problems=tag_problem_queries,
        )
