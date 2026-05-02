import pytest
from unittest.mock import MagicMock, AsyncMock

from app.recommendation.infra.repository.level_filter_repository_impl import LevelFilterRepositoryImpl


def _make_repo(mock_database_context) -> LevelFilterRepositoryImpl:
    return LevelFilterRepositoryImpl(db=mock_database_context)


class TestLevelFilterRepository:
    """LevelFilterRepositoryImpl 테스트"""

    async def test_find_all_active_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_all_active()

        assert result == []
