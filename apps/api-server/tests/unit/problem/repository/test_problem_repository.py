import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.vo.identifiers import ProblemId
from app.problem.infra.repository.problem_repository_impl import ProblemRepositoryImpl


def _make_problem_model(problem_id=1000, title="A+B"):
    model = MagicMock()
    model.problem_id = problem_id
    model.title = title
    model.tier_level = 5
    model.class_level = 0
    model.solved_user_count = 100
    model.problem_tags = []
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    model.deleted_at = None
    return model


def _make_repo(mock_database_context) -> ProblemRepositoryImpl:
    return ProblemRepositoryImpl(db=mock_database_context)


class TestProblemRepository:
    """ProblemRepositoryImpl 테스트"""

    async def test_find_by_ids_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_by_ids([])

        assert result == []

    async def test_find_by_id_prefix_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        # Default mock scalars().all() returns []
        result = await repo.find_by_id_prefix("9999")

        assert result == []

    async def test_find_by_title_keyword_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_by_title_keyword("nonexistent")

        assert result == []
