from typing import override
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.common.domain.vo.identifiers import UserAccountId
from app.common.domain.enums import Provider
from app.core.database import Database
from app.user.domain.entity.user_account import UserAccount
from app.user.domain.repository.user_account_repository import UserAccountRepository
from app.user.infra.mapper.user_account_mapper import UserAccountMapper
from app.user.infra.mapper.account_link_mapper import AccountLinkMapper
from app.user.infra.model.user_account import UserAccountModel
from app.user.infra.model.account_link import AccountLinkModel

class UserAccountRepositoryImpl(UserAccountRepository):
    """유저 계정 Repository"""
    
    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()
    
    @override
    async def insert(self, user_account: UserAccount) -> UserAccount:
        """유저 저장"""
            
        # 새 회원 생성
        model = UserAccountMapper.to_model(user_account)
        self.session.add(model)
        
        await self.session.flush()  # ID 생성을 위해 flush
        
        # 생성된 ID를 엔티티에 설정
        return UserAccountMapper.to_entity(model)
    
    @override
    async def find_by_id(self, user_id: UserAccountId) -> UserAccount | None:
        stmt = (
            select(UserAccountModel)
            .options(
                joinedload(UserAccountModel.account_links),
                joinedload(UserAccountModel.targets)
            )
            .where(
                and_(
                    UserAccountModel.user_account_id == user_id.value,
                    UserAccountModel.deleted_at.is_(None)
                )
            )
        )
        result = await self.session.execute(stmt)
        model = result.unique().scalars().one_or_none()
        
        return UserAccountMapper.to_entity(model) if model else None

    @override
    async def find_by_provider(
        self, 
        provider: Provider, 
        provider_id: str
    ) -> UserAccount | None:
        """Provider 정보로 유저 조회 (연관된 account_links 포함)"""
        stmt = (
            select(UserAccountModel)
            .options(
                # Mapper에서 model.account_links에 접근하므로 미리 로드함
                joinedload(UserAccountModel.account_links),
                joinedload(UserAccountModel.targets),
            )
            .where(
                and_(
                    UserAccountModel.provider == provider,
                    UserAccountModel.provider_id == provider_id,
                    UserAccountModel.deleted_at.is_(None)
                )
            )
        )
        
        result = await self.session.execute(stmt)
        model = result.unique().scalars().one_or_none()
        
        return UserAccountMapper.to_entity(model) if model else None
    
    @override
    async def exists_by_id(self, user_id: UserAccountId) -> bool:
        """유저 존재 여부 확인"""
        stmt = select(UserAccountModel).where(
            and_(
                UserAccountModel.user_account_id == user_id.value,
                UserAccountModel.deleted_at.is_(None)
            )
        )
        result = await self.session.execute(stmt)
        exists = result.scalar_one_or_none() is not None

        return exists

    async def update(self, user_account: UserAccount) -> None:
        # 1. 엔티티를 (자식이 포함된) 모델로 변환
        model = UserAccountMapper.to_model(user_account)

        # 2. 세션에 병합
        await self.session.merge(model)

        # 3. 변경사항 확정
        await self.session.flush()

    async def delete(self, user_account: UserAccount) -> None:
        """
        사용자 계정 삭제 (Hard Delete)
        연관 데이터(targets, account_links)도 함께 삭제
        """
        from sqlalchemy import delete
        from app.user.infra.model.user_target import UserTargetModel
        from app.user.infra.model.account_link import AccountLinkModel

        user_id_value = user_account.user_account_id.value

        # 1. user_target 삭제
        await self.session.execute(
            delete(UserTargetModel).where(UserTargetModel.user_account_id == user_id_value)
        )

        # 2. account_link 삭제
        await self.session.execute(
            delete(AccountLinkModel).where(AccountLinkModel.user_account_id == user_id_value)
        )

        # 3. user_account 삭제
        await self.session.execute(
            delete(UserAccountModel).where(UserAccountModel.user_account_id == user_id_value)
        )

    async def delete_all_by_provider(self, provider: Provider) -> int:
        """
        특정 Provider의 모든 유저 삭제 (Hard Delete)

        CASCADE 삭제 순서:
        1. bj_account 관련 (problem_history, tag_skill_history, scheduler_log)
        2. activity 관련 (user_date_record, problem_record, will_solve_problem, problem_banned_record, tag_customization)
        3. account_link
        4. user_target
        5. user_account
        """
        from sqlalchemy import delete, select
        from app.user.infra.model.user_target import UserTargetModel
        from app.user.infra.model.account_link import AccountLinkModel
        from app.baekjoon.infra.model.bj_account import BjAccountModel
        from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
        from app.baekjoon.infra.model.scheduler_log import SchedulerLogModel
        from app.baekjoon.infra.model.tag_skill_history import TagSkillHistoryModel
        from app.activity.infra.model.user_problem_status import UserProblemStatusModel
        from app.activity.infra.model.tag_custom import TagCustomModel
        from app.activity.infra.model.user_date_record import UserDateRecordModel

        # 1. Provider.NONE인 유저 ID 목록 조회
        stmt = select(UserAccountModel.user_account_id).where(
            UserAccountModel.provider == provider.value
        )
        result = await self.session.execute(stmt)
        user_ids = [row[0] for row in result.all()]

        if not user_ids:
            return 0

        # 2. account_link로 연결된 bj_account_id 목록 조회
        stmt = select(AccountLinkModel.bj_account_id).where(
            AccountLinkModel.user_account_id.in_(user_ids)
        )
        result = await self.session.execute(stmt)
        bj_account_ids = [row[0] for row in result.all()]

        # 3. bj_account 관련 데이터 삭제
        if bj_account_ids:
            await self.session.execute(
                delete(ProblemHistoryModel).where(ProblemHistoryModel.bj_account_id.in_(bj_account_ids))
            )
            await self.session.execute(
                delete(TagSkillHistoryModel).where(TagSkillHistoryModel.bj_account_id.in_(bj_account_ids))
            )
            await self.session.execute(
                delete(SchedulerLogModel).where(SchedulerLogModel.bj_account_id.in_(bj_account_ids))
            )
            await self.session.execute(
                delete(BjAccountModel).where(BjAccountModel.bj_account_id.in_(bj_account_ids))
            )

        # 4. activity 관련 데이터 삭제 (UserProblemStatusModel 삭제 시 ProblemDateRecordModel CASCADE 삭제)
        await self.session.execute(
            delete(UserDateRecordModel).where(UserDateRecordModel.user_account_id.in_(user_ids))
        )
        await self.session.execute(
            delete(UserProblemStatusModel).where(UserProblemStatusModel.user_account_id.in_(user_ids))
        )
        await self.session.execute(
            delete(TagCustomModel).where(TagCustomModel.user_account_id.in_(user_ids))
        )

        # 5. account_link 삭제
        await self.session.execute(
            delete(AccountLinkModel).where(AccountLinkModel.user_account_id.in_(user_ids))
        )

        # 6. user_target 삭제
        await self.session.execute(
            delete(UserTargetModel).where(UserTargetModel.user_account_id.in_(user_ids))
        )

        # 7. user_account 삭제
        result = await self.session.execute(
            delete(UserAccountModel).where(UserAccountModel.user_account_id.in_(user_ids))
        )

        return len(user_ids)