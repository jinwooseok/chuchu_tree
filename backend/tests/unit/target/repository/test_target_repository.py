import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock

from app.common.domain.vo.identifiers import TargetId
from app.target.infra.repository.target_repository_impl import TargetRepositoryImpl


def _make_target_model(target_id=1, code="COTE", display_name="코딩테스트 준비"):
    model = MagicMock()
    model.target_id = target_id
    model.target_code = code
    model.target_display_name = display_name
    model.active_yn = True
    model.target_tags = []
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    model.deleted_at = None
    return model


def _make_repo(mock_database_context) -> TargetRepositoryImpl:
    return TargetRepositoryImpl(db=mock_database_context)


class TestTargetRepository:
    """TargetRepositoryImpl 테스트"""

    async def test_find_by_id_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_target_model()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        target = await repo.find_by_id(TargetId(1))

        assert target is not None
        assert target.code == "COTE"

    async def test_find_by_id_not_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = None
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        target = await repo.find_by_id(TargetId(999))

        assert target is None

    async def test_find_by_code(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_target_model()

        result_mock = MagicMock()
        result_mock.scalar_one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        target = await repo.find_by_code("COTE")

        assert target is not None
        assert target.code == "COTE"

    async def test_find_all_active(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        models = [_make_target_model(1, "COTE"), _make_target_model(2, "PS")]

        # 첫 번째 execute: 타겟 목록 조회
        target_scalars = MagicMock()
        target_scalars.all.return_value = models
        target_result = MagicMock()
        target_result.scalars.return_value = target_scalars

        # 두 번째 execute: 타겟 태그 조회 (빈 목록)
        tag_scalars = MagicMock()
        tag_scalars.all.return_value = []
        tag_result = MagicMock()
        tag_result.scalars.return_value = tag_scalars

        mock_database_context.get_current_session().execute = AsyncMock(
            side_effect=[target_result, tag_result]
        )

        targets = await repo.find_all_active()

        assert len(targets) == 2
