from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Database
from app.study.domain.repository.user_search_repository import UserSearchRepository, UserSearchResult
from app.user.infra.model.account_link import AccountLinkModel
from app.user.infra.model.user_account import UserAccountModel


class UserSearchRepositoryImpl(UserSearchRepository):
    def __init__(self, db: Database):
        self.db = db

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    async def search_by_keyword(self, keyword: str, limit: int = 5) -> list[UserSearchResult]:
        stmt = (
            select(
                UserAccountModel.user_account_id,
                UserAccountModel.user_code,
                UserAccountModel.profile_image,
                AccountLinkModel.bj_account_id,
            )
            .join(
                AccountLinkModel,
                and_(
                    AccountLinkModel.user_account_id == UserAccountModel.user_account_id,
                    AccountLinkModel.deleted_at.is_(None),
                ),
            )
            .where(
                and_(
                    UserAccountModel.deleted_at.is_(None),
                    or_(
                        AccountLinkModel.bj_account_id.like(f"%{keyword}%"),
                        UserAccountModel.user_code.like(f"%{keyword}%"),
                    ),
                )
            )
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            UserSearchResult(
                user_account_id=row.user_account_id,
                bj_account_id=row.bj_account_id,
                user_code=row.user_code,
                profile_image=row.profile_image,
            )
            for row in rows
        ]

    async def find_by_user_account_id(self, user_account_id: int) -> UserSearchResult | None:
        stmt = (
            select(
                UserAccountModel.user_account_id,
                UserAccountModel.user_code,
                UserAccountModel.profile_image,
                AccountLinkModel.bj_account_id,
            )
            .join(
                AccountLinkModel,
                and_(
                    AccountLinkModel.user_account_id == UserAccountModel.user_account_id,
                    AccountLinkModel.deleted_at.is_(None),
                ),
            )
            .where(
                and_(
                    UserAccountModel.user_account_id == user_account_id,
                    UserAccountModel.deleted_at.is_(None),
                )
            )
        )
        result = await self.session.execute(stmt)
        row = result.one_or_none()
        if row is None:
            return None
        return UserSearchResult(
            user_account_id=row.user_account_id,
            bj_account_id=row.bj_account_id,
            user_code=row.user_code,
            profile_image=row.profile_image,
        )

    async def find_by_user_account_ids(self, ids: list[int]) -> list[UserSearchResult]:
        if not ids:
            return []
        stmt = (
            select(
                UserAccountModel.user_account_id,
                UserAccountModel.user_code,
                UserAccountModel.profile_image,
                AccountLinkModel.bj_account_id,
            )
            .join(
                AccountLinkModel,
                and_(
                    AccountLinkModel.user_account_id == UserAccountModel.user_account_id,
                    AccountLinkModel.deleted_at.is_(None),
                ),
            )
            .where(
                and_(
                    UserAccountModel.user_account_id.in_(ids),
                    UserAccountModel.deleted_at.is_(None),
                )
            )
        )
        result = await self.session.execute(stmt)
        rows = result.all()
        return [
            UserSearchResult(
                user_account_id=row.user_account_id,
                bj_account_id=row.bj_account_id,
                user_code=row.user_code,
                profile_image=row.profile_image,
            )
            for row in rows
        ]
