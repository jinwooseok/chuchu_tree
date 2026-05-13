"""Target Repository 구현"""
from typing import override

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.vo.identifiers import TargetId
from app.core.database import Database
from app.target.domain.entity.target import Target
from app.target.domain.repository.target_repository import TargetRepository
from app.target.infra.mapper.target_mapper import TargetMapper
from app.target.infra.mapper.target_tag_mapper import TargetTagMapper
from app.target.infra.model.target import TargetModel
from app.target.infra.model.target_tag import TargetTagModel


class TargetRepositoryImpl(TargetRepository):
    """Target Repository 구현체"""

    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    @override
    async def save(self, target: Target) -> Target:
        """목표 저장 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_by_id(self, target_id: TargetId) -> Target | None:
        """ID로 목표 조회 (구현 필요)"""
        stmt = select(TargetModel).where(
            and_(
                TargetModel.target_id == target_id.value,
                TargetModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return TargetMapper.to_entity(model) if model else None

    @override
    async def find_by_code(self, code: str) -> Target | None:
        """코드로 목표 조회 (구현 필요)"""
        stmt = select(TargetModel).where(
            and_(
                TargetModel.target_code == code,
                TargetModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        model = result.scalar_one_or_none()

        return TargetMapper.to_entity(model) if model else None

    @override
    async def find_all_active(self) -> list[Target]:
        """모든 활성화된 목표 조회"""
        # 1. 활성 타겟 조회
        target_stmt = (
            select(TargetModel)
            .where(
                and_(
                    TargetModel.active_yn == True,
                    TargetModel.deleted_at.is_(None)
                )
            )
        )

        target_result = await self.session.execute(target_stmt)
        target_models = target_result.scalars().all()

        if not target_models:
            return []

        # 2. 타겟 ID 목록 추출
        target_ids = [model.target_id for model in target_models]

        # 3. 타겟 태그 조회
        tag_stmt = (
            select(TargetTagModel)
            .where(
                and_(
                    TargetTagModel.target_id.in_(target_ids),
                    TargetTagModel.deleted_at.is_(None)
                )
            )
        )

        tag_result = await self.session.execute(tag_stmt)
        tag_models = tag_result.scalars().all()

        # 4. 타겟별 태그 매핑
        target_tags_map = {}
        for tag_model in tag_models:
            if tag_model.target_id not in target_tags_map:
                target_tags_map[tag_model.target_id] = []
            target_tags_map[tag_model.target_id].append(
                TargetTagMapper.to_entity(tag_model)
            )

        # 5. Entity 변환
        targets = []
        for target_model in target_models:
            required_tags = target_tags_map.get(target_model.target_id, [])
            target = TargetMapper.to_entity(target_model, required_tags=required_tags)
            targets.append(target)

        return targets

    @override
    async def exists_by_code(self, code: str) -> bool:
        """코드 존재 여부 확인 (구현 필요)"""
        raise NotImplementedError()

    @override
    async def find_by_ids(self, target_ids: list[TargetId]) -> list[Target]:
        """여러 ID로 목표 조회 (구현 필요)"""
        raise NotImplementedError()
