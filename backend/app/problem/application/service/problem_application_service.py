"""Problem Application Service"""
import logging

from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
from app.common.domain.vo.identifiers import ProblemId, TagId, TargetId
from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.problem.application.query.problems_info_query import (
    ProblemInfoQuery,
    ProblemsInfoQuery,
    TagAliasQuery,
    TagInfoQuery,
    TagTargetQuery
)
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.tag.domain.repository.tag_repository import TagRepository
from app.target.domain.repository.target_repository import TargetRepository
from app.tier.domain.repository.tier_repository import TierRepository

logger = logging.getLogger(__name__)

@event_register_handlers()
class ProblemApplicationService:
    """Problem Application Service"""

    def __init__(
        self,
        problem_repository: ProblemRepository,
        tag_repository: TagRepository,
        target_repository: TargetRepository,
        tier_repository: TierRepository
    ):
        self.problem_repository = problem_repository
        self.tag_repository = tag_repository
        self.target_repository = target_repository
        self.tier_repository = tier_repository

    @event_handler("GET_PROBLEMS_INFO_REQUESTED")
    @transactional
    async def get_problems_info(
        self,
        payload: GetProblemsInfoPayload
    ) -> ProblemsInfoQuery:
        """
        문제 정보 조회 (태그, 타겟 정보 포함)
        Args:
            payload: 문제 정보 조회 요청
        Returns:
            ProblemsInfoQuery: 문제 정보 목록
        """
        if not payload.problem_ids:
            return ProblemsInfoQuery(problems={})

        # 1. 문제 ID 목록으로 문제 조회 (태그 포함)
        problem_ids = [ProblemId(pid) for pid in payload.problem_ids]
        problems = await self.problem_repository.find_by_ids(problem_ids)

        # 2. 모든 태그 ID 수집
        tag_ids_set = set()
        for problem in problems:
            for problem_tag in problem.tags:
                tag_ids_set.add(problem_tag.tag_id)

        # 3. 태그 정보 조회
        tag_ids = list(tag_ids_set)
        tags = await self.tag_repository.find_by_ids_and_active(tag_ids) if tag_ids else []
        tag_map = {tag.tag_id.value: tag for tag in tags}

        # 5. 모든 타겟 조회 (태그별 필터링을 위해)
        all_targets = await self.target_repository.find_all_active()
        
        # 6. 태그별 타겟 매핑 생성
        tag_targets_map = {}  # tag_id -> list[Target]
        for target in all_targets:
            for target_tag in target.required_tags:
                if target_tag.tag_id.value not in tag_targets_map:
                    tag_targets_map[target_tag.tag_id.value] = []
                tag_targets_map[target_tag.tag_id.value].append(target)

        # 7. Tier 정보 조회 (tier_level -> tier_name 매핑)
        tier_map = {}
        for problem in problems:
            if problem.tier_level.value not in tier_map:
                tier = await self.tier_repository.find_by_level(problem.tier_level.value)
                if tier:
                    tier_map[problem.tier_level.value] = tier.tier_code

        # 8. Query 객체로 변환
        problems_dict = {}
        for problem in problems:
            # 태그 정보 조립
            tag_queries = []
            for problem_tag in problem.tags:
                tag = tag_map.get(problem_tag.tag_id.value)
                if tag:
                    # 태그 별칭
                    tag_aliases = [TagAliasQuery(alias=alias) for alias in tag.aliases]

                    # 태그 타겟
                    tag_targets = tag_targets_map.get(tag.tag_id.value, [])
                    tag_target_queries = [
                        TagTargetQuery(
                            target_id=target.target_id.value,
                            target_code=target.code,
                            target_display_name=target.display_name
                        )
                        for target in tag_targets
                    ]

                    tag_queries.append(TagInfoQuery(
                        tag_id=tag.tag_id.value,
                        tag_code=tag.code,
                        tag_display_name=tag.tag_display_name,
                        tag_aliases=tag_aliases,
                        tag_targets=tag_target_queries
                    ))

            # 문제 정보
            problem_query = ProblemInfoQuery(
                problem_id=problem.problem_id.value,
                problem_title=problem.title,
                problem_tier_level=problem.tier_level.value,
                problem_tier_name=tier_map.get(problem.tier_level.value, "Unknown"),
                problem_class_level=problem.class_level,
                tags=tag_queries
            )
            problems_dict[problem.problem_id.value] = problem_query

        return ProblemsInfoQuery(problems=problems_dict)
