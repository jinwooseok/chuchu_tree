import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.enums import Provider
from app.common.domain.vo.identifiers import UserAccountId, BaekjoonAccountId, TargetId
from app.core.exception import APIException
from app.user.application.command.user_account_command import CreateUserAccountCommand, DeleteUserAccountCommand
from app.user.application.command.link_bj_account_command import LinkBjAccountCommand
from app.user.application.command.get_user_account_info_command import GetUserAccountInfoCommand
from app.user.application.command.update_user_target_command import UpdateUserTargetCommand
from app.user.application.service.user_account_application_service import UserAccountApplicationService
from app.user.domain.entity.user_account import UserAccount


def _make_service(
    repo_return=None,
    event_bus_return=None
) -> UserAccountApplicationService:
    repo = AsyncMock()
    if repo_return is not None:
        repo.find_by_provider.return_value = repo_return
        repo.find_by_id.return_value = repo_return
    event_bus = AsyncMock()
    if event_bus_return is not None:
        event_bus.publish.return_value = event_bus_return

    service = UserAccountApplicationService(
        user_account_repository=repo,
        domain_event_bus=event_bus,
    )
    return service


def _make_existing_user(user_id: int = 1) -> UserAccount:
    now = datetime.now()
    return UserAccount(
        user_account_id=UserAccountId(user_id),
        provider=Provider.KAKAO,
        provider_id="kakao_123",
        email="old@example.com",
        profile_image=None,
        registered_at=now,
        created_at=now,
        updated_at=now,
        account_links=[],
        targets=[],
    )


class TestCreateOrFindUserAccount:
    """create_or_find_user_account() 테스트"""

    async def test_existing_user_returns_not_new(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = CreateUserAccountCommand(
            provider="KAKAO",
            provider_id="kakao_123",
            email="old@example.com"
        )

        result = await service.create_or_find_user_account(command)

        assert result.new_user_yn is False
        assert result.user_account_id == 1

    async def test_existing_user_email_updated(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = CreateUserAccountCommand(
            provider="KAKAO",
            provider_id="kakao_123",
            email="new@example.com"
        )

        await service.create_or_find_user_account(command)

        service.user_account_repository.update.assert_called_once()

    async def test_new_user_created(self, mock_database_context):
        service = _make_service(repo_return=None)
        new_user = _make_existing_user(user_id=99)
        service.user_account_repository.find_by_provider.return_value = None
        service.user_account_repository.insert.return_value = new_user

        command = CreateUserAccountCommand(
            provider="KAKAO",
            provider_id="new_kakao_id",
            email="new@example.com"
        )

        result = await service.create_or_find_user_account(command)

        assert result.new_user_yn is True
        assert result.user_account_id == 99
        service.user_account_repository.insert.assert_called_once()


class TestLinkBaekjoonAccount:
    """link_baekjoon_account() 테스트"""

    async def test_link_success(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = LinkBjAccountCommand(
            user_account_id=1,
            bj_account_id="test_bj"
        )

        result = await service.link_baekjoon_account(command)

        assert result is True
        service.user_account_repository.update.assert_called_once()

    async def test_link_user_not_found_raises(self, mock_database_context):
        service = _make_service(repo_return=None)
        service.user_account_repository.find_by_id.return_value = None

        command = LinkBjAccountCommand(
            user_account_id=999,
            bj_account_id="test_bj"
        )

        with pytest.raises(APIException) as exc_info:
            await service.link_baekjoon_account(command)

        assert exc_info.value.error_code == "INVALID_REQUEST"


class TestGetUserAccountInfo:
    """get_user_account_info() 테스트"""

    async def test_get_info_success(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = GetUserAccountInfoCommand(user_account_id=1)

        result = await service.get_user_account_info(command)

        assert result.user_account_id == 1
        assert result.provider == "KAKAO"

    async def test_get_info_user_not_found_raises(self, mock_database_context):
        service = _make_service(repo_return=None)
        service.user_account_repository.find_by_id.return_value = None

        command = GetUserAccountInfoCommand(user_account_id=999)

        with pytest.raises(APIException) as exc_info:
            await service.get_user_account_info(command)

        assert exc_info.value.error_code == "INVALID_REQUEST"


class TestDeleteUserAccount:
    """delete_user_account() 테스트"""

    async def test_delete_success(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = DeleteUserAccountCommand(user_account_id=1)

        result = await service.delete_user_account(command)

        assert result is True
        service.user_account_repository.delete.assert_called_once()

    async def test_delete_user_not_found_returns_false(self, mock_database_context):
        service = _make_service(repo_return=None)
        service.user_account_repository.find_by_id.return_value = None

        command = DeleteUserAccountCommand(user_account_id=999)

        result = await service.delete_user_account(command)

        assert result is False


class TestUpdateUserTarget:
    """update_user_target() 테스트"""

    async def test_update_target_success(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        # Mock event bus response for target info
        target_info = MagicMock()
        target_info.target_id = 1
        target_info.target_code = "COTE"
        target_info.target_display_name = "코딩테스트"
        service.domain_event_bus.publish.return_value = target_info

        command = UpdateUserTargetCommand(
            user_account_id=1,
            target_code="COTE"
        )

        await service.update_user_target(command)

        service.user_account_repository.update.assert_called_once()

    async def test_update_target_user_not_found(self, mock_database_context):
        service = _make_service(repo_return=None)
        service.user_account_repository.find_by_id.return_value = None

        command = UpdateUserTargetCommand(
            user_account_id=999,
            target_code="COTE"
        )

        with pytest.raises(APIException) as exc_info:
            await service.update_user_target(command)

        assert exc_info.value.error_code == "INVALID_REQUEST"
