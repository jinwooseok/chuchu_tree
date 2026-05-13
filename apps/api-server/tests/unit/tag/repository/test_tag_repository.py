import pytest
from datetime import datetime
from unittest.mock import MagicMock, AsyncMock, patch

from app.common.domain.enums import TagLevel
from app.common.domain.vo.identifiers import TagId
from app.tag.infra.repository.tag_repository_impl import TagRepositoryImpl


def _make_tag_model(tag_id=1, code="dp", tag_display_name="다이나믹 프로그래밍", level=TagLevel.REQUIREMENT):
    model = MagicMock()
    model.tag_id = tag_id
    model.tag_code = code
    model.tag_display_name = tag_display_name
    model.tag_level = level.value
    model.excluded_yn = False
    model.excluded_reason = None
    model.min_solved_person_count = 0
    model.aliases = []
    model.tag_problem_count = 100
    model.created_at = datetime.now()
    model.updated_at = datetime.now()
    model.deleted_at = None
    return model


def _make_repo(mock_database_context) -> TagRepositoryImpl:
    return TagRepositoryImpl(db=mock_database_context)


def _mock_inspect(unloaded=None):
    """sqlalchemy.inspect를 대체할 mock - unloaded 속성 제공"""
    if unloaded is None:
        unloaded = {"parent_tag_relations", "targets"}
    mock_ins = MagicMock()
    mock_ins.unloaded = unloaded
    return lambda obj: mock_ins


class TestTagRepository:
    """TagRepositoryImpl 테스트"""

    async def test_find_by_id_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_tag_model()

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        with patch('app.tag.infra.mapper.tag_mapper.inspect', _mock_inspect()):
            tag = await repo.find_by_id(TagId(1))

        assert tag is not None
        assert tag.code == "dp"

    async def test_find_by_id_not_found(self, mock_database_context):
        repo = _make_repo(mock_database_context)

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = None
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        tag = await repo.find_by_id(TagId(999))

        assert tag is None

    async def test_find_by_code(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        model = _make_tag_model()

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.one_or_none.return_value = model
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        with patch('app.tag.infra.mapper.tag_mapper.inspect', _mock_inspect()):
            tag = await repo.find_by_code("dp")

        assert tag is not None
        assert tag.code == "dp"

    async def test_find_active_tags(self, mock_database_context):
        repo = _make_repo(mock_database_context)
        models = [_make_tag_model(1, "dp"), _make_tag_model(2, "greedy")]

        result_mock = MagicMock()
        result_mock.unique.return_value.scalars.return_value.fetchall.return_value = models
        mock_database_context.get_current_session().execute = AsyncMock(return_value=result_mock)

        with patch('app.tag.infra.mapper.tag_mapper.inspect', _mock_inspect()):
            tags = await repo.find_active_tags()

        assert len(tags) == 2
