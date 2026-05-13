import pytest
from datetime import date, datetime
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.vo.identifiers import BaekjoonAccountId
from app.baekjoon.infra.repository.streak_repository_impl import StreakRepositoryImpl


def _make_repo(mock_database_context) -> StreakRepositoryImpl:
    return StreakRepositoryImpl(db=mock_database_context)


class TestStreakRepository:
    """StreakRepositoryImpl 테스트"""

    async def test_find_by_account_and_date_range_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        # Default mock returns empty
        result = await repo.find_by_account_and_date_range(
            bj_account_id=BaekjoonAccountId("test_bj"),
            start_date=date(2025, 1, 1),
            end_date=date(2025, 1, 31),
        )

        assert result == []
