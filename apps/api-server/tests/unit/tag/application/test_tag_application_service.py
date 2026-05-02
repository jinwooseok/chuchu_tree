import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.enums import TagLevel
from app.common.domain.vo.identifiers import TagId
from app.core.exception import APIException
from app.tag.application.command.tag_command import GetTagInfoCommand, GetTagInfosCommand
from app.tag.application.service.tag_application_service import TagApplicationService
from app.tag.domain.entity.tag import Tag
from app.tag.domain.vo.tag_exclusion import TagExclusion


def _make_tag(tag_id: int = 1, code: str = "dp") -> Tag:
    now = datetime.now()
    return Tag(
        tag_id=TagId(tag_id),
        code=code,
        tag_display_name="다이나믹 프로그래밍",
        level=TagLevel.REQUIREMENT,
        exclusion=TagExclusion.is_not_excluded(),
        min_solved_person_count=0,
        aliases=[],
        problem_count=100,
        created_at=now,
        updated_at=now,
    )


def _make_service() -> TagApplicationService:
    repo = AsyncMock()
    return TagApplicationService(tag_repository=repo)


class TestGetTags:
    """get_tags() 이벤트 핸들러 테스트"""

    async def test_get_tags_success(self, mock_database_context):
        service = _make_service()
        tags = [_make_tag(1, "dp"), _make_tag(2, "greedy")]
        service.tag_repository.find_by_ids.return_value = tags

        command = GetTagInfosCommand(tag_ids=[TagId(1), TagId(2)])
        result = await service.get_tags(command)

        assert len(result.tags) == 2
        assert result.tags[0].tag_code == "dp"
        assert result.tags[1].tag_code == "greedy"

    async def test_get_tags_empty(self, mock_database_context):
        service = _make_service()
        service.tag_repository.find_by_ids.return_value = []

        command = GetTagInfosCommand(tag_ids=[])
        result = await service.get_tags(command)

        assert result.tags == []


class TestGetTagByCommand:
    """get_tag_by_command() 이벤트 핸들러 테스트"""

    async def test_get_by_id(self, mock_database_context):
        service = _make_service()
        tag = _make_tag(1, "dp")
        service.tag_repository.find_by_id.return_value = tag

        command = GetTagInfoCommand(tag_id=TagId(1), tag_code=None)
        result = await service.get_tag_by_command(command)

        assert result.tag_id == 1
        assert result.tag_code == "dp"

    async def test_get_by_code(self, mock_database_context):
        service = _make_service()
        tag = _make_tag(1, "dp")
        service.tag_repository.find_by_code.return_value = tag

        command = GetTagInfoCommand(tag_id=None, tag_code="dp")
        result = await service.get_tag_by_command(command)

        assert result.tag_code == "dp"

    async def test_tag_not_found_raises(self, mock_database_context):
        service = _make_service()
        service.tag_repository.find_by_code.return_value = None

        command = GetTagInfoCommand(tag_id=None, tag_code="nonexistent")

        with pytest.raises(APIException) as exc_info:
            await service.get_tag_by_command(command)

        assert exc_info.value.error_code == "TAG_NOT_FOUND"
