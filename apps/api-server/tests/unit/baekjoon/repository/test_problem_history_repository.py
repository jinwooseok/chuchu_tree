import pytest
from datetime import date
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.vo.identifiers import BaekjoonAccountId, UserAccountId
from app.baekjoon.infra.repository.problem_history_repository_impl import ProblemHistoryRepositoryImpl


def _make_repo(mock_database_context) -> ProblemHistoryRepositoryImpl:
    return ProblemHistoryRepositoryImpl(db=mock_database_context)


class TestProblemHistoryRepository:
    """ProblemHistoryRepositoryImpl 테스트"""

    async def test_find_solved_ids_by_bj_account_id_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_solved_ids_by_bj_account_id(BaekjoonAccountId("test_bj"))

        assert result == set() or result == []

    async def test_find_unrecorded_problem_ids_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_unrecorded_problem_ids(
            user_account_id=UserAccountId(1),
            bj_account_id=BaekjoonAccountId("test_bj"),
        )

        assert len(result) == 0
