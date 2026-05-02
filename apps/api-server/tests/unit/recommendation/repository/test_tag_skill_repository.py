import pytest
from unittest.mock import MagicMock, AsyncMock

from app.recommendation.infra.repository.tag_skill_repository_impl import TagSkillRepositoryImpl


def _make_repo(mock_database_context) -> TagSkillRepositoryImpl:
    return TagSkillRepositoryImpl(db=mock_database_context)


class TestTagSkillRepository:
    """TagSkillRepositoryImpl 테스트"""

    async def test_find_all_active_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_all_active()

        assert result == []
