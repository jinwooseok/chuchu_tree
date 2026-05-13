import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.vo.identifiers import TierId
from app.tier.infra.repository.tier_repository_impl import TierRepositoryImpl


def _make_tier_model(tier_id=1, tier_level=10, tier_code="Silver V", tier_rating=800):
    model = MagicMock()
    model.tier_id = tier_id
    model.tier_level = tier_level
    model.tier_code = tier_code
    model.tier_rating = tier_rating
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    model.deleted_at = None
    return model


def _make_repo(mock_database_context) -> TierRepositoryImpl:
    return TierRepositoryImpl(db=mock_database_context)


class TestTierRepository:
    """TierRepositoryImpl 테스트"""

    async def test_find_by_id_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_tier_model()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        tier = await repo.find_by_id(TierId(1))

        assert tier is not None
        assert tier.tier_code == "Silver V"
        assert tier.tier_level == 10

    async def test_find_by_id_not_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        tier = await repo.find_by_id(TierId(999))

        assert tier is None

    async def test_find_all(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        models = [_make_tier_model(1, 10, "Silver V"), _make_tier_model(2, 15, "Gold V")]

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = models
        result_mock = MagicMock()
        result_mock.scalars.return_value = scalars_mock
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        tiers = await repo.find_all()

        assert len(tiers) == 2
        assert tiers[0].tier_code == "Silver V"
        assert tiers[1].tier_code == "Gold V"

    async def test_find_by_levels(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        models = [_make_tier_model(1, 10, "Silver V")]

        scalars_mock = MagicMock()
        scalars_mock.all.return_value = models
        result_mock = MagicMock()
        result_mock.scalars.return_value = scalars_mock
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        tiers = await repo.find_by_levels([10])

        assert len(tiers) == 1

    async def test_find_by_levels_empty(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        tiers = await repo.find_by_levels([])

        assert tiers == []

    async def test_find_by_level(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_tier_model()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        tier = await repo.find_by_level(10)

        assert tier is not None
        assert tier.tier_level == 10

    async def test_find_by_code(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_tier_model()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        tier = await repo.find_by_code("Silver V")

        assert tier is not None
        assert tier.tier_code == "Silver V"
