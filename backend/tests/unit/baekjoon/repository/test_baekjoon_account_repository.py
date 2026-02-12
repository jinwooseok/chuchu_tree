import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId, TierId
from app.baekjoon.infra.repository.baekjoon_account_repository_impl import BaekjoonAccountRepositoryImpl


def _make_bj_model(bj_account_id="test_bj"):
    model = MagicMock()
    model.bj_account_id = bj_account_id
    model.tier_id = 10
    model.rating = 1500
    model.contribution_count = 0
    model.class_ = 3
    model.longest_streak = 50
    model.tier_start_date = datetime.now()
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    model.deleted_at = None
    model.problem_histories = []
    model.streaks = []
    model.tier_histories = []
    model.tag_skill_histories = []
    return model


def _make_repo(mock_database_context) -> BaekjoonAccountRepositoryImpl:
    return BaekjoonAccountRepositoryImpl(db=mock_database_context)


class TestBaekjoonAccountRepository:
    """BaekjoonAccountRepositoryImpl 테스트"""

    async def test_find_by_id_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_bj_model()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        account = await repo.find_by_id(BaekjoonAccountId("test_bj"))

        assert account is not None
        assert account.bj_account_id.value == "test_bj"

    async def test_find_by_id_not_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        account = await repo.find_by_id(BaekjoonAccountId("unknown"))

        assert account is None

    async def test_find_all(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        models = [_make_bj_model("user1"), _make_bj_model("user2")]

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = models
        result_mock = MagicMock()
        result_mock.scalars.return_value = scalars_mock
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        accounts = await repo.find_all()

        assert len(accounts) == 2
