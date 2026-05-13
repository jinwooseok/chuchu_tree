import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.enums import Provider
from app.common.domain.vo.identifiers import UserAccountId
from app.user.infra.repository.user_account_repository_impl import UserAccountRepositoryImpl


def _make_user_model(user_account_id=1, provider=Provider.KAKAO, provider_id="kakao_123"):
    model = MagicMock()
    model.user_account_id = user_account_id
    model.provider = provider
    model.provider_id = provider_id
    model.email = "test@example.com"
    model.profile_image = None
    model.registered_at = datetime.now()
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    model.deleted_at = None
    model.account_links = []
    model.targets = []
    return model


def _make_repo(mock_database_context) -> UserAccountRepositoryImpl:
    return UserAccountRepositoryImpl(db=mock_database_context)


class TestUserAccountRepository:
    """UserAccountRepositoryImpl 테스트"""

    async def test_find_by_id_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_user_model()

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        user = await repo.find_by_id(UserAccountId(1))

        assert user is not None
        assert user.provider == Provider.KAKAO

    async def test_find_by_id_not_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        user = await repo.find_by_id(UserAccountId(999))

        assert user is None

    async def test_find_by_provider_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_user_model()

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        user = await repo.find_by_provider(Provider.KAKAO, "kakao_123")

        assert user is not None

    async def test_exists_by_id_true(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = 1
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        exists = await repo.exists_by_id(UserAccountId(1))

        assert exists is True

    async def test_exists_by_id_false(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        exists = await repo.exists_by_id(UserAccountId(999))

        assert exists is False
