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

    @override
    async def update(self, user_account: UserAccount) -> UserAccount:
        """유저 업데이트"""
        # 기존 유저 모델 조회
        stmt = (
            select(UserAccountModel)
            .options(
                joinedload(UserAccountModel.account_links),
                joinedload(UserAccountModel.targets)
            )
            .where(UserAccountModel.user_account_id == user_account.user_account_id.value)
        )
        result = await self.session.execute(stmt)
        existing_model = result.unique().scalars().one_or_none()

        # 기본 정보 업데이트
        existing_model.provider = user_account.provider
        existing_model.provider_id = user_account.provider_id
        existing_model.profile_image = user_account.profile_image
        existing_model.registered_at = user_account.registered_at
        existing_model.updated_at = user_account.updated_at
        existing_model.deleted_at = user_account.deleted_at

        # AccountLink 저장
        for link in user_account.account_links:
            link_model = AccountLinkMapper.to_model(link)
            self.session.add(link_model)

        await self.session.flush()

        return UserAccountMapper.to_entity(existing_model)