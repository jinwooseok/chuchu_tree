"""User Application Service"""

import logging

from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import BaekjoonAccountId, TargetId, UserAccountId
from app.common.infra.event.decorators import event_register_handlers, event_handler
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.user.application.command.link_bj_account_command import LinkBjAccountCommand
from app.user.application.command.update_user_target_command import UpdateUserTargetCommand
from app.user.application.command.user_account_command import CreateUserAccountCommand
from app.user.application.command.get_user_account_info_command import GetUserAccountInfoCommand
from app.user.application.query.user_account_query import CreateUserAccountQuery
from app.user.application.query.user_account_info_query import GetUserAccountInfoQuery
from app.user.application.query.user_tags_query import TargetQuery
from app.user.domain.entity.user_account import UserAccount
from app.user.domain.entity.user_target import UserTarget
from app.user.domain.event.payloads import GetTargetInfoPayload, GetTargetInfoResultPayload
from app.user.domain.repository.user_account_repository import UserAccountRepository
from app.common.domain.enums import Provider

logger = logging.getLogger(__name__)


@event_register_handlers()
class UserAccountApplicationService:
    """
    User 도메인 Application Service
    """

    def __init__(
        self,
        user_account_repository: UserAccountRepository,
        domain_event_bus: DomainEventBus
    ):
        self.user_account_repository = user_account_repository
        self.domain_event_bus = domain_event_bus

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
    
    @event_handler("LINK_BAEKJOON_ACCOUNT_REQUESTED")
    async def link_baekjoon_account(
        self,
        command: LinkBjAccountCommand
    ) -> bool:
        """
        백준 계정 연동

        Args:
            user_account_id: 유저 계정 ID
            bj_account_id: 백준 유저 ID (닉네임)

        Returns:
            bool: 연동 성공 여부
        """

        # 1. 유저 계정 조회
        user_account = await self.user_account_repository.find_by_id(UserAccountId(command.user_account_id))
        if not user_account:
            raise APIException(ErrorCode.INVALID_REQUEST)

        # 3. UserAccount 엔티티에 연동 정보 기록
        bj_account_id = BaekjoonAccountId(command.bj_account_id)
        user_account.link_baekjoon_account(bj_account_id)

        # 4. 저장
        await self.user_account_repository.update(user_account)

        return True

    @event_handler("GET_USER_ACCOUNT_INFO_REQUESTED")
    async def get_user_account_info(
        self,
        command: GetUserAccountInfoCommand
    ) -> GetUserAccountInfoQuery:
        """
        유저 계정 정보 조회

        Args:
            command: 유저 계정 정보 조회 명령

        Returns:
            GetUserAccountInfoQuery: 유저 계정 정보
        """
        # 유저 계정 조회
        user_account = await self.user_account_repository.find_by_id(
            UserAccountId(command.user_account_id)
        )

        if not user_account:
            raise APIException(ErrorCode.INVALID_REQUEST)

        return GetUserAccountInfoQuery(
            user_account_id=user_account.user_account_id.value,
            provider=user_account.provider.value,
            targets=user_account.targets,
            profile_image=user_account.profile_image,
            registered_at=user_account.registered_at
        )
    
    @transactional
    async def get_user_target(self, user_account_id: int):
        user_account = await self.user_account_repository.find_by_id(
            UserAccountId(user_account_id)
        )
        if user_account.targets:
            event = DomainEvent(
                event_type="GET_TARGET_INFO_REQUESTED",
                data=GetTargetInfoPayload(target_id=user_account.targets[0].target_id.value),
                result_type=GetTargetInfoResultPayload
            )
            
            target_info: TargetQuery = await self.domain_event_bus.publish(event)
            
            query = TargetQuery(
                target_id=target_info.target_id,
                target_code=target_info.target_code,
                target_display_name=target_info.target_display_name
            )
            
        else:
            query = TargetQuery()
        return query
    
    @transactional
    async def update_user_target(self, command: UpdateUserTargetCommand):
        user_account = await self.user_account_repository.find_by_id(
            UserAccountId(command.user_account_id)
        )
    
        if not user_account:
            raise APIException(ErrorCode.INVALID_REQUEST)
        
        # 받은 목표 코드의 정보를 이벤트로 요청함.
        event = DomainEvent(
            event_type="GET_TARGET_INFO_REQUESTED",
            data=GetTargetInfoPayload(target_code=command.target_code),
            result_type=GetTargetInfoResultPayload
        )

        target_info: TargetQuery = await self.domain_event_bus.publish(event)
        print(user_account.targets)
        user_account.set_target(TargetId(value=target_info.target_id))
        print(user_account.targets)
        await self.user_account_repository.update(user_account)