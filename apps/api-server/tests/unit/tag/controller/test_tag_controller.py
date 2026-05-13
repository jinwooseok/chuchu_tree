import pytest
from unittest.mock import AsyncMock

from app.core.api_response import ApiResponse
from app.tag.presentation.controller.tag_controller import get_all_tags


class TestTagController:
    """Tag Controller 단위 테스트 - 함수 직접 호출"""

    async def test_get_all_tags_returns_api_response(self):
        result = await get_all_tags()
        assert isinstance(result, ApiResponse)
