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