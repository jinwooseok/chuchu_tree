import pytest
from datetime import date
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.vo.identifiers import UserAccountId
from app.activity.infra.repository.user_activity_repository_impl import UserActivityRepositoryImpl


def _make_repo(mock_database_context) -> UserActivityRepositoryImpl:
    return UserActivityRepositoryImpl(db=mock_database_context)


class TestUserActivityRepository:
    """UserActivityRepositoryImpl 테스트"""

    async def test_find_will_solve_problems_by_date_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_will_solve_problems_by_date(
            user_id=UserAccountId(1),
            target_date=date(2025, 1, 15),
        )

        assert result == []

    async def test_find_problem_records_by_date_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_problem_records_by_date(
            user_id=UserAccountId(1),
            target_date=date(2025, 1, 15),
        )

        assert result == []

    async def test_find_problem_records_by_problem_ids_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result = await repo.find_problem_records_by_problem_ids(
            user_id=UserAccountId(1),
            problem_ids=[],
        )

        assert result == []
