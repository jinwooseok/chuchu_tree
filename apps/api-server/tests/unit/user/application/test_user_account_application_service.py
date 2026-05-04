import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.enums import Provider
from app.common.domain.vo.identifiers import UserAccountId, BaekjoonAccountId, TargetId
from app.core.exception import APIException
from app.user.application.command.user_account_command import CreateUserAccountCommand, DeleteUserAccountCommand
from app.user.application.command.link_bj_account_command import LinkBjAccountCommand
from app.user.application.command.get_user_account_info_command import GetUserAccountInfoCommand
from app.user.application.command.mark_synced_command import MarkSyncedCommand
from app.user.application.command.update_user_target_command import UpdateUserTargetCommand
from app.user.application.service.user_account_application_service import UserAccountApplicationService
from app.user.domain.entity.account_link import AccountLink
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


class TestLinkBaekjoonAccountWithProblemCount:
    """link_baekjoon_account() - problem_count에 따른 is_synced 테스트"""

    async def test_link_with_problems_sets_is_synced_false(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = LinkBjAccountCommand(
            user_account_id=1,
            bj_account_id="test_bj",
            problem_count=100
        )

        result = await service.link_baekjoon_account(command)

        assert result is True
        # 연동된 link의 is_synced가 False인지 확인
        updated_user = service.user_account_repository.update.call_args[0][0]
        active_link = next(l for l in updated_user.account_links if l.deleted_at is None)
        assert active_link.is_synced is False

    async def test_link_without_problems_sets_is_synced_true(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = LinkBjAccountCommand(
            user_account_id=1,
            bj_account_id="test_bj",
            problem_count=0
        )

        result = await service.link_baekjoon_account(command)

        assert result is True
        updated_user = service.user_account_repository.update.call_args[0][0]
        active_link = next(l for l in updated_user.account_links if l.deleted_at is None)
        assert active_link.is_synced is True


class TestMarkAccountLinkSynced:
    """mark_account_link_synced() - BATCH_SYNC_COMPLETED 이벤트 핸들러 테스트"""

    async def test_mark_synced_success(self, mock_database_context):
        existing = _make_existing_user()
        # 활성 AccountLink 추가 (is_synced=False)
        existing.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=BaekjoonAccountId("test_bj"),
                created_at=datetime.now(),
                deleted_at=None,
                is_synced=False
            )
        )
        service = _make_service(repo_return=existing)

        command = MarkSyncedCommand(user_account_id=1)
        await service.mark_account_link_synced(command)

        service.user_account_repository.update.assert_called_once()
        updated_user = service.user_account_repository.update.call_args[0][0]
        active_link = next(l for l in updated_user.account_links if l.deleted_at is None)
        assert active_link.is_synced is True

    async def test_mark_synced_user_not_found_no_error(self, mock_database_context):
        service = _make_service(repo_return=None)
        service.user_account_repository.find_by_id.return_value = None

        command = MarkSyncedCommand(user_account_id=999)

        # user가 없어도 에러 없이 반환
        await service.mark_account_link_synced(command)
        service.user_account_repository.update.assert_not_called()

    async def test_mark_synced_no_active_link(self, mock_database_context):
        existing = _make_existing_user()
        # 삭제된 링크만 있는 경우
        existing.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=BaekjoonAccountId("test_bj"),
                created_at=datetime.now(),
                deleted_at=datetime.now(),
                is_synced=False
            )
        )
        service = _make_service(repo_return=existing)

        command = MarkSyncedCommand(user_account_id=1)
        await service.mark_account_link_synced(command)

        # 활성 링크가 없으므로 is_synced 변경 없음
        service.user_account_repository.update.assert_called_once()


class TestGetUserAccountInfoIsSynced:
    """get_user_account_info() - is_synced 필드 반환 테스트"""

    async def test_info_includes_is_synced_true(self, mock_database_context):
        existing = _make_existing_user()
        existing.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=BaekjoonAccountId("test_bj"),
                created_at=datetime.now(),
                deleted_at=None,
                is_synced=True
            )
        )
        service = _make_service(repo_return=existing)

        command = GetUserAccountInfoCommand(user_account_id=1)
        result = await service.get_user_account_info(command)

        assert result.is_synced is True

    async def test_info_includes_is_synced_false(self, mock_database_context):
        existing = _make_existing_user()
        existing.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=BaekjoonAccountId("test_bj"),
                created_at=datetime.now(),
                deleted_at=None,
                is_synced=False
            )
        )
        service = _make_service(repo_return=existing)

        command = GetUserAccountInfoCommand(user_account_id=1)
        result = await service.get_user_account_info(command)

        assert result.is_synced is False

    async def test_info_no_link_returns_is_synced_false(self, mock_database_context):
        existing = _make_existing_user()
        service = _make_service(repo_return=existing)

        command = GetUserAccountInfoCommand(user_account_id=1)
        result = await service.get_user_account_info(command)

        assert result.is_synced is False
