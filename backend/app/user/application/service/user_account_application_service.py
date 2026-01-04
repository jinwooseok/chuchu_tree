"""User Application Service"""

import logging

from app.common.infra.event.decorators import event_register_handlers, event_handler
from app.user.application.command.user_account_command import CreateUserAccountCommand
from app.user.application.query.user_account_query import CreateUserAccountQuery
from app.user.domain.entity.user_account import UserAccount
from app.user.domain.repository.user_account_repository import UserAccountRepository
from app.common.domain.enums import Provider

logger = logging.getLogger(__name__)


@event_register_handlers()
class UserAccountApplicationService:
    """
    User 도메인 Application Service
    """

    def __init__(self, user_account_repository: UserAccountRepository):
        self.user_account_repository = user_account_repository

    @event_handler("SOCIAL_LOGIN_SUCCESSED")
    async def create_or_find_user_account(
        self,
        command: CreateUserAccountCommand
    ) -> CreateUserAccountQuery:
        """
        사용자 계정을 생성하거나 조회함
        """

        # 1. Provider enum 변환
        provider = Provider(command.provider)

        # 2. 기존 사용자 조회
        existing_user = await self.user_account_repository.find_by_provider(
            provider=provider,
            provider_id=command.provider_id
        )
        
        # 유저가 이미 존재한다면 새로운 유저가 아님을 알림
        if existing_user:
            return CreateUserAccountQuery(
                user_account_id=existing_user.user_account_id.value,
                new_user_yn=False
            )

        # 3. 신규 사용자 생성
        new_user = UserAccount.create(
            provider=provider,
            provider_id=command.provider_id
        )

        saved_user = await self.user_account_repository.insert(new_user)

        return CreateUserAccountQuery(
            user_account_id=saved_user.user_account_id.value,
            new_user_yn=True
        )