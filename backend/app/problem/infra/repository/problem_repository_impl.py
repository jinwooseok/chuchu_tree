"""Problem Repository 구현"""
from typing import override

from sqlalchemy import String, and_, cast, select
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

    async def _attach_tags_and_map_to_entities(self, problem_models: list[ProblemModel]) -> list[Problem]:
        """조회된 ProblemModel 리스트에 태그를 붙여 Entity로 변환합니다."""
        if not problem_models:
            return []

        problem_id_values = [pm.problem_id for pm in problem_models]

        # 1. 문제 태그 통합 조회 (In-clause)
        tag_stmt = (
            select(ProblemTagModel)
            .where(ProblemTagModel.problem_id.in_(problem_id_values))
        )
        tag_result = await self.session.execute(tag_stmt)
        tag_models = tag_result.scalars().all()

        # 2. 문제별 태그 매핑
        problem_tags_map = {}
        for tag_model in tag_models:
            if tag_model.problem_id not in problem_tags_map:
                problem_tags_map[tag_model.problem_id] = []
            problem_tags_map[tag_model.problem_id].append(
                ProblemTagMapper.to_entity(tag_model)
            )

        # 3. Entity 변환 및 반환
        return [
            ProblemMapper.to_entity(pm, tags=problem_tags_map.get(pm.problem_id, []))
            for pm in problem_models
        ]

    @override
    async def find_by_ids(self, problem_ids: list[ProblemId]) -> list[Problem]:
        """기존 로직을 프라이빗 메서드 재사용으로 간소화"""
        if not problem_ids: return []
        
        problem_id_values = [pid.value for pid in problem_ids]
        stmt = select(ProblemModel).where(
            and_(ProblemModel.problem_id.in_(problem_id_values), ProblemModel.deleted_at.is_(None))
        )
        result = await self.session.execute(stmt)
        return await self._attach_tags_and_map_to_entities(result.scalars().all())

    @override
    async def find_by_id_prefix(self, prefix: str, limit: int = 5) -> list[Problem]:
        """ID 프리픽스 검색 시에도 태그 포함하여 반환"""
        stmt = (
            select(ProblemModel)
            .where(
                and_(
                    cast(ProblemModel.problem_id, String).like(f"{prefix}%"),
                    ProblemModel.deleted_at.is_(None)
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        # 태그 부착 로직 호출
        return await self._attach_tags_and_map_to_entities(result.scalars().all())

    @override
    async def find_by_title_keyword(self, keyword: str, limit: int = 5) -> list[Problem]:
        """제목 키워드 검색 시에도 태그 포함하여 반환"""
        stmt = (
            select(ProblemModel)
            .where(
                and_(
                    ProblemModel.problem_title.contains(keyword),
                    ProblemModel.deleted_at.is_(None)
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        # 태그 부착 로직 호출
        return await self._attach_tags_and_map_to_entities(result.scalars().all())

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

    @override
    async def find_recommended_problem(
        self,
        tag_id: TagId,
        tier_range: 'TierRange',
        skill_rate: int,
        min_solved_count: int,
        exclude_ids: set[int],
        priority_ids: set[int]
    ) -> Problem | None:
        """추천 문제 조회"""
        from app.common.domain.vo.primitives import TierRange

        # 1. 기본 쿼리 구성: 태그 필터링
        stmt = (
            select(ProblemModel)
            .join(ProblemTagModel, ProblemModel.problem_id == ProblemTagModel.problem_id)
            .where(
                and_(
                    ProblemTagModel.tag_id == tag_id.value,
                    ProblemModel.deleted_at.is_(None)
                )
            )
        )

        # 2. 티어 범위 필터링
        if tier_range.min_tier_id is not None:
            stmt = stmt.where(ProblemModel.problem_tier_level >= tier_range.min_tier_id.value)
        if tier_range.max_tier_id is not None:
            stmt = stmt.where(ProblemModel.problem_tier_level <= tier_range.max_tier_id.value)

        # 3. 제외 문제 필터링
        if exclude_ids:
            stmt = stmt.where(ProblemModel.problem_id.notin_(exclude_ids))

        # 4. 우선순위 문제 먼저 조회
        if priority_ids:
            priority_stmt = stmt.where(ProblemModel.problem_id.in_(priority_ids)).limit(1)
            priority_result = await self.session.execute(priority_stmt)
            priority_problem = priority_result.scalar_one_or_none()

            if priority_problem:
                problems = await self._attach_tags_and_map_to_entities([priority_problem])
                return problems[0] if problems else None

        # 5. 일반 문제 조회 (랜덤하게 하나 선택)
        # TODO: min_solved_count 조건 추가 필요 (Problem 테이블에 solved_count 필드 추가 후)
        # TODO: skill_rate 기반 난이도 필터링 구현 필요
        stmt = stmt.order_by(ProblemModel.problem_id).limit(1)
        result = await self.session.execute(stmt)
        problem_model = result.scalar_one_or_none()

        if not problem_model:
            return None

        problems = await self._attach_tags_and_map_to_entities([problem_model])
        return problems[0] if problems else None

