"""User Application Service"""

import logging

from app.common.domain.entity.domain_event import DomainEvent
from app.common.domain.gateway.storage_gateway import StorageGateway
from app.common.domain.service.event_publisher import DomainEventBus
from app.common.domain.vo.identifiers import BaekjoonAccountId, TargetId, UserAccountId
from app.common.infra.event.decorators import event_register_handlers, event_handler
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.user.application.command.link_bj_account_command import LinkBjAccountCommand
from app.user.application.command.mark_synced_command import MarkSyncedCommand
from app.user.application.command.update_user_target_command import UpdateUserTargetCommand
from app.user.application.command.user_account_command import CreateUserAccountCommand, DeleteUserAccountCommand
from app.user.application.command.get_user_account_info_command import GetUserAccountInfoCommand
from app.user.application.query.user_account_query import CreateUserAccountQuery
from app.user.application.query.user_account_info_query import GetUserAccountInfoQuery
from app.user.application.query.user_tags_query import TargetQuery
from app.user.domain.entity.user_account import UserAccount
from app.user.domain.entity.user_target import UserTarget
from app.user.domain.event.payloads import GetTargetInfoPayload, GetTargetInfoResultPayload
from app.user.domain.repository.user_account_repository import UserAccountRepository
from app.common.domain.enums import Provider
from app.core.database import transactional

logger = logging.getLogger(__name__)

DEFAULT_PROFILE_IMAGE_PATH = "default-user-image.svg"


@event_register_handlers()
class UserAccountApplicationService:
    """
    User 도메인 Application Service
    """

    def __init__(
        self,
        user_account_repository: UserAccountRepository,
        domain_event_bus: DomainEventBus,
        storage_gateway: StorageGateway,
    ):
        self.user_account_repository = user_account_repository
        self.domain_event_bus = domain_event_bus
        self.storage_gateway = storage_gateway

    @event_handler("SOCIAL_LOGIN_SUCCESSED")
    @transactional
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
            # 기존 사용자의 이메일 업데이트 (변경된 경우만)
            if command.email and existing_user.email != command.email:
                existing_user.email = command.email
                existing_user.updated_at = existing_user.updated_at  # Mapper에서 자동으로 갱신될 수도 있음
                await self.user_account_repository.update(existing_user)

            return CreateUserAccountQuery(
                user_account_id=existing_user.user_account_id.value,
                new_user_yn=False
            )

        # 3. 신규 사용자 생성
        new_user = UserAccount.create(
            provider=provider,
            provider_id=command.provider_id,
            email=command.email
        )
        new_user.update_profile_image(DEFAULT_PROFILE_IMAGE_PATH)

        saved_user = await self.user_account_repository.insert(new_user)

        return CreateUserAccountQuery(
            user_account_id=saved_user.user_account_id.value,
            new_user_yn=True
        )
    
    @event_handler("LINK_BAEKJOON_ACCOUNT_REQUESTED")
    @transactional
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
        user_account.link_baekjoon_account(bj_account_id, problem_count=command.problem_count)

        # 4. 저장
        await self.user_account_repository.update(user_account)

        return True

    @event_handler("BATCH_SYNC_COMPLETED")
    @transactional
    async def mark_account_link_synced(
        self,
        command: MarkSyncedCommand
    ) -> None:
        """배치 동기화 완료 시 활성 AccountLink의 is_synced를 True로 설정"""
        user_account = await self.user_account_repository.find_by_id(
            UserAccountId(command.user_account_id)
        )
        if not user_account:
            return

        # 활성 AccountLink 찾아서 synced 처리
        for link in user_account.account_links:
            if link.deleted_at is None:
                link.mark_as_synced()

        await self.user_account_repository.update(user_account)

    @event_handler("GET_USER_ACCOUNT_INFO_REQUESTED")
    @transactional(readonly=True)
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
        user_account: UserAccount = await self.user_account_repository.find_by_id(
            UserAccountId(command.user_account_id)
        )
        
        if not user_account:
            raise APIException(ErrorCode.INVALID_REQUEST)
        
        if user_account.targets:
            target_info = await self.get_user_target(user_account.user_account_id.value)
        else:
            target_info = None
            
        # 활성 AccountLink의 is_synced 값 조회
        active_link = next(
            (link for link in user_account.account_links if link.deleted_at is None),
            None
        )
        is_synced = active_link.is_synced if active_link else False

        profile_image_url = None
        if user_account.profile_image:
            profile_image_url = await self.storage_gateway.generate_presigned_url(user_account.profile_image)
        if not profile_image_url:
            profile_image_url = await self.storage_gateway.generate_presigned_url(DEFAULT_PROFILE_IMAGE_PATH)

        return GetUserAccountInfoQuery(
            user_account_id=user_account.user_account_id.value,
            provider=user_account.provider.value,
            targets=[target_info] if target_info else [],
            profile_image_url=profile_image_url,
            registered_at=user_account.registered_at,
            is_synced=is_synced,
            user_code=user_account.user_code,
        )
    
    @transactional(readonly=True)
    async def get_user_target(self, user_account_id: int):
        user_account = await self.user_account_repository.find_by_id(
            UserAccountId(user_account_id)
        )
        if user_account.targets:
            event = DomainEvent(
                event_type="GET_TARGET_INFO_REQUESTED",
                data=GetTargetInfoPayload(target_id=user_account._get_current_target().target_id.value),
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

    @transactional
    async def set_profile_image(
        self,
        user_account_id: int,
        file_content: bytes,
        file_name: str,
        content_type: str,
    ) -> str:
        """프로필 이미지 업로드 후 presigned URL 반환"""
        user_account = await self.user_account_repository.find_by_id(UserAccountId(user_account_id))
        if not user_account:
            raise APIException(ErrorCode.INVALID_REQUEST)

        if user_account.profile_image and user_account.profile_image != DEFAULT_PROFILE_IMAGE_PATH:
            await self.storage_gateway.delete_file(user_account.profile_image)

        path_prefix = f"profile-images/{user_account_id}/"
        relative_path, _ = await self.storage_gateway.upload_file(
            file_content=file_content,
            file_name=file_name,
            content_type=content_type,
            path_prefix=path_prefix,
        )

        user_account.update_profile_image(relative_path)
        await self.user_account_repository.update(user_account)

        presigned_url = await self.storage_gateway.generate_presigned_url(relative_path)
        return presigned_url

    @transactional
    async def delete_profile_image(self, user_account_id: int) -> None:
        """프로필 이미지 삭제"""
        user_account = await self.user_account_repository.find_by_id(UserAccountId(user_account_id))
        if not user_account:
            raise APIException(ErrorCode.INVALID_REQUEST)

        if user_account.profile_image and user_account.profile_image != DEFAULT_PROFILE_IMAGE_PATH:
            await self.storage_gateway.delete_file(user_account.profile_image)
        user_account.update_profile_image(DEFAULT_PROFILE_IMAGE_PATH)
        await self.user_account_repository.update(user_account)

    @event_handler("USER_ACCOUNT_WITHDRAWAL_REQUESTED")
    @transactional
    async def delete_user_account(
        self,
        command: DeleteUserAccountCommand
    ) -> bool:
        """
        사용자 계정 삭제 (Hard Delete)

        Args:
            command: 사용자 계정 삭제 명령

        Returns:
            bool: 삭제 성공 여부
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 1. 사용자 계정 조회
        user_account = await self.user_account_repository.find_by_id(user_account_id)
        if not user_account:
            logger.warning(f"삭제할 사용자를 찾을 수 없음: user_account_id={command.user_account_id}")
            return False

        # 2. 사용자 계정 삭제 (Hard Delete)
        await self.user_account_repository.delete(user_account)
        logger.info(f"UserAccount 삭제 완료: user_id={command.user_account_id}")

        return True

    @event_handler("TEST_USERS_CLEANUP_REQUESTED")
    @transactional
    async def cleanup_test_users(self, command: dict) -> dict:
        """
        테스트 유저 일괄 삭제 (Provider.NONE인 모든 유저)

        Args:
            command: {"provider": "NONE"}

        Returns:
            {"deleted_count": int}
        """
        provider_str = command.get("provider")
        provider = Provider(provider_str)

        deleted_count = await self.user_account_repository.delete_all_by_provider(provider)

        logger.info(f"테스트 유저 일괄 삭제 완료: provider={provider_str}, count={deleted_count}")

        return {"deleted_count": deleted_count}