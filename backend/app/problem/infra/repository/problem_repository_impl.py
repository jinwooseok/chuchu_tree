"""Problem Repository 구현"""
from typing import override

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.vo.identifiers import ProblemId, TagId
from app.common.domain.vo.primitives import TierLevel
from app.core.database import Database
from app.problem.domain.entity.problem import Problem
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.problem.infra.mapper.problem_mapper import ProblemMapper
from app.problem.infra.mapper.problem_tag_mapper import ProblemTagMapper
from app.problem.infra.model.problem import ProblemModel
from app.problem.infra.model.problem_tag import ProblemTagModel


class ProblemRepositoryImpl(ProblemRepository):
    """Problem Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, problem: Problem) -> Problem:
        """문제 저장 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_by_id(self, problem_id: ProblemId) -> Problem | None:
        """문제 ID로 조회 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_by_ids(self, problem_ids: list[ProblemId]) -> list[Problem]:
        """여러 문제 ID로 조회 (태그 포함)"""
        if not problem_ids:
            return []

        # 1. 문제 정보 조회
        problem_id_values = [pid.value for pid in problem_ids]
        problem_stmt = (
            select(ProblemModel)
            .where(
                and_(
                    ProblemModel.problem_id.in_(problem_id_values),
                    ProblemModel.deleted_at.is_(None)
                )
            )
        )

        problem_result = await self.session.execute(problem_stmt)
        problem_models = problem_result.scalars().all()

        # 2. 문제 태그 조회
        tag_stmt = (
            select(ProblemTagModel)
            .where(ProblemTagModel.problem_id.in_(problem_id_values))
        )

        tag_result = await self.session.execute(tag_stmt)
        tag_models = tag_result.scalars().all()

        # 3. 문제별 태그 매핑
        problem_tags_map = {}
        for tag_model in tag_models:
            if tag_model.problem_id not in problem_tags_map:
                problem_tags_map[tag_model.problem_id] = []
            problem_tags_map[tag_model.problem_id].append(
                ProblemTagMapper.to_entity(tag_model)
            )

        # 4. Entity 변환
        problems = []
        for problem_model in problem_models:
            tags = problem_tags_map.get(problem_model.problem_id, [])
            problem = ProblemMapper.to_entity(problem_model, tags=tags)
            problems.append(problem)

        return problems

    @override
    async def find_by_tier_range(
        self,
        min_tier: TierLevel,
        max_tier: TierLevel
    ) -> list[Problem]:
        """티어 범위로 조회 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_by_tags(self, tag_ids: list[TagId]) -> list[Problem]:
        """태그로 조회 (구현 필요)"""
        raise NotImplementedError()
