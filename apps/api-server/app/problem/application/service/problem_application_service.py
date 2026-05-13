"""Problem Application Service"""
import asyncio
import logging

from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
from app.common.domain.vo.identifiers import ProblemId
from app.common.infra.event.decorators import event_handler, event_register_handlers
from app.core.database import transactional
from app.problem.application.query.problems_info_query import (
    ProblemInfoQuery,
    ProblemsInfoQuery,
    TagAliasQuery,
    TagInfoQuery,
    TagTargetQuery
)
from app.problem.domain.entity.problem import Problem
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.tag.domain.entity.tag import Tag
from app.tag.domain.repository.tag_repository import TagRepository
from app.target.domain.entity.target import Target
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

    @event_handler("GET_PROBLEM_INFOS_REQUESTED")
    @transactional(readonly=True)
    async def get_problems_info(self, payload: GetProblemsInfoPayload) -> ProblemsInfoQuery:
        """단일 진입점: 문제 ID 목록으로 상세 정보 조회"""
        problems = await self._get_base_data(payload.problem_ids)
        return await self._get_problems_info_logic(problems)
    
    @transactional(readonly=True)
    async def search_problem_by_keyword(self, keyword: str) -> list[list[ProblemInfoQuery]]:
        """검색 진입점: 키워드 검색 후 결과를 ID기준/제목기준으로 분리하여 반환"""
        # 1. 레포지토리 병렬 검색 (동일 세션 공유)
        id_models = await self.problem_repository.find_by_id_prefix(keyword, limit=5)
        title_models = await self.problem_repository.find_by_title_keyword(keyword, limit=5)


        all_ids = list({p.problem_id.value for p in id_models + title_models})
        if not all_ids:
            return [[], []]

        all_models = list({p.problem_id.value: p for p in id_models + title_models}.values())
        detailed_info = await self._get_problems_info_logic(all_models)
        details_map = detailed_info.problems
        
        # 3. 결과 매핑
        id_base_queries = [details_map[m.problem_id.value] for m in id_models if m.problem_id.value in details_map]
        title_base_queries = [details_map[m.problem_id.value] for m in title_models if m.problem_id.value in details_map]

        return [id_base_queries, title_base_queries]

    # --- [Internal Business Logic: No Decorators] ---

    async def _get_problems_info_logic(self, problems: list[Problem]) -> ProblemsInfoQuery:
        """
        실제 데이터 Fetch 및 조립을 담당하는 핵심 로직.
        """
        if not problems:
            return ProblemsInfoQuery(problems={})

        # 기존 쪼개놓은 하위 비동기 함수들 호출
        all_targets = await self.target_repository.find_all_active()
        tag_map = await self._get_tag_map(problems)
        tier_map = await self._get_tier_map(problems)
        tag_targets_map = await self._create_tag_targets_map(all_targets)

        problems_dict = {}
        for problem in problems:
            problems_dict[problem.problem_id.value] = self._compose_problem_query(
                problem, tag_map, tag_targets_map, tier_map
            )

        return ProblemsInfoQuery(problems=problems_dict)
        
    async def _get_base_data(self, problem_ids: list[str]):
        """기초 데이터(문제, 모든 타겟)를 조회합니다."""
        p_ids = [ProblemId(pid) for pid in problem_ids]
        problems = await self.problem_repository.find_by_ids(p_ids)
        return problems

    async def _get_tag_map(self, problems: list[Problem]) -> dict[str, Tag]:
        """문제들에 포함된 태그들을 조회하여 맵으로 반환합니다."""
        tag_ids_set = {pt.tag_id for p in problems for pt in p.tags}
        tag_ids = list(tag_ids_set)
        
        tags = await self.tag_repository.find_by_ids_and_active(tag_ids) if tag_ids else []
        return {tag.tag_id.value: tag for tag in tags}

    async def _get_tier_map(self, problems: list[Problem]) -> dict[int, str]:
        unique_levels = list({p.tier_level.value for p in problems})
        if not unique_levels:
            return {}
        
        # 루프 대신 IN 쿼리 하나로 해결 (리포지토리에 find_by_levels 구현 가정)
        tiers = await self.tier_repository.find_by_levels(unique_levels) 
        return {t.tier_level: t.tier_code for t in tiers}
    
    async def _create_tag_targets_map(self, all_targets: list[Target]) -> dict[str, list[Target]]:
        """태그 ID별로 연관된 타겟 목록을 매핑합니다."""
        tag_targets_map = {}
        for target in all_targets:
            for target_tag in target.required_tags:
                tag_id_val = target_tag.tag_id.value
                if tag_id_val not in tag_targets_map:
                    tag_targets_map[tag_id_val] = []
                tag_targets_map[tag_id_val].append(target)
        return tag_targets_map
    
    def _compose_problem_query(
        self, 
        problem: Problem, 
        tag_map: dict, 
        tag_targets_map: dict, 
        tier_map: dict
    ) -> ProblemInfoQuery:
        """단일 문제에 대한 쿼리 객체를 생성합니다 (Pure function 스타일)"""
        tag_queries = []
        for problem_tag in problem.tags:
            tag: Tag = tag_map.get(problem_tag.tag_id.value)
            if not tag:
                continue

            # 태그 별칭 및 타겟 변환
            tag_aliases = [TagAliasQuery(alias=alias['alias']) for alias in tag.aliases]
            tag_targets = [
                TagTargetQuery(
                    target_id=t.target_id.value,
                    target_code=t.code,
                    target_display_name=t.display_name
                ) for t in tag_targets_map.get(tag.tag_id.value, [])
            ]

            tag_queries.append(TagInfoQuery(
                tag_id=tag.tag_id.value,
                tag_code=tag.code,
                tag_display_name=tag.tag_display_name,
                tag_aliases=tag_aliases,
                tag_targets=tag_targets
            ))

        return ProblemInfoQuery(
            problem_id=problem.problem_id.value,
            problem_title=problem.title,
            problem_tier_level=problem.tier_level.value,
            problem_tier_name=tier_map.get(problem.tier_level.value, "Unknown"),
            problem_class_level=problem.class_level,
            tags=tag_queries
        )