import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.vo.identifiers import TargetId, TagId
from app.core.exception import APIException
from app.target.application.command.target_command import GetTargetInfoCommand
from app.target.application.service.target_application_service import TargetApplicationService
from app.target.domain.entity.target import Target


def _make_target(target_id: int = 1, code: str = "COTE", display_name: str = "코딩테스트 준비") -> Target:
    now = datetime.now()
    target = Target(
        target_id=TargetId(target_id),
        code=code,
        display_name=display_name,
        active=True,
        required_tags=[],
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )
    return target


def _make_service() -> TargetApplicationService:
    repo = AsyncMock()
    return TargetApplicationService(target_repository=repo)


class TestGetAllTargets:
    """get_all_targets() 테스트"""

    async def test_get_all_active_targets(self, mock_database_context):
        service = _make_service()
        targets = [_make_target(1, "COTE"), _make_target(2, "PS", "PS 대회 준비")]
        service.target_repository.find_all_active.return_value = targets

        result = await service.get_all_targets()

        assert len(result) == 2
        assert result[0].target_code == "COTE"
        assert result[1].target_code == "PS"

    async def test_get_all_targets_empty(self, mock_database_context):
        service = _make_service()
        service.target_repository.find_all_active.return_value = []

        result = await service.get_all_targets()

        assert result == []

    async def test_get_targets_by_ids(self, mock_database_context):
        service = _make_service()
        targets = [_make_target(1, "COTE")]
        service.target_repository.find_by_ids.return_value = targets

        result = await service.get_all_targets(target_ids=[1])

        assert len(result) == 1
        service.target_repository.find_by_ids.assert_called_once_with(target_ids=[1])
        service.target_repository.find_all_active.assert_not_called()


class TestGetTargetByCommand:
    """get_target_by_command() 테스트"""

    async def test_get_by_id(self, mock_database_context):
        service = _make_service()
        target = _make_target(1, "COTE")
        service.target_repository.find_by_id.return_value = target

        command = GetTargetInfoCommand(target_id=1, target_code=None)
        result = await service.get_target_by_command(command)

        assert result.target_id == 1
        assert result.target_code == "COTE"

    async def test_get_by_code(self, mock_database_context):
        service = _make_service()
        target = _make_target(1, "COTE")
        service.target_repository.find_by_code.return_value = target

        command = GetTargetInfoCommand(target_id=None, target_code="COTE")
        result = await service.get_target_by_command(command)

        assert result.target_code == "COTE"
        assert result.target_display_name == "코딩테스트 준비"
