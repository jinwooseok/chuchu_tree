import pytest
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock

from app.common.domain.vo.identifiers import ProblemId, TagId, TargetId
from app.problem.application.service.problem_application_service import ProblemApplicationService
from app.problem.domain.entity.problem import Problem
from app.tag.domain.entity.tag import Tag
from app.target.domain.entity.target import Target
from app.common.domain.enums import TagLevel
from app.tag.domain.vo.tag_exclusion import TagExclusion


def _make_service() -> ProblemApplicationService:
    return ProblemApplicationService(
        problem_repository=AsyncMock(),
        tag_repository=AsyncMock(),
        target_repository=AsyncMock(),
        tier_repository=AsyncMock(),
    )


def _make_problem(problem_id: int = 1000, title: str = "A+B", tier_level: int = 1) -> Problem:
    now = datetime.now()
    return Problem(
        problem_id=ProblemId(problem_id),
        title=title,
        tier_level=MagicMock(value=tier_level),
        class_level=0,
        solved_user_count=100,
        tags=[],
        created_at=now,
        updated_at=now,
    )


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


def _make_target(target_id: int = 1, code: str = "COTE") -> Target:
    now = datetime.now()
    return Target(
        target_id=TargetId(target_id),
        code=code,
        display_name="코딩테스트 준비",
        active=True,
        required_tags=[],
        deleted_at=None,
        created_at=now,
        updated_at=now,
    )


class TestSearchProblemByKeyword:
    """search_problem_by_keyword() 테스트"""

    async def test_search_returns_empty_when_no_results(self, mock_database_context):
        service = _make_service()
        service.problem_repository.find_by_id_prefix.return_value = []
        service.problem_repository.find_by_title_keyword.return_value = []

        result = await service.search_problem_by_keyword("nonexistent")

        assert result == [[], []]

    async def test_search_by_id_prefix(self, mock_database_context):
        service = _make_service()
        problem = _make_problem(1000, "A+B")
        service.problem_repository.find_by_id_prefix.return_value = [problem]
        service.problem_repository.find_by_title_keyword.return_value = []
        service.target_repository.find_all_active.return_value = []
        service.tag_repository.find_by_ids_and_active.return_value = []
        service.tier_repository.find_by_levels.return_value = []

        result = await service.search_problem_by_keyword("1000")

        assert len(result) == 2
        assert len(result[0]) == 1  # id-based results
        assert result[0][0].problem_id == 1000

    async def test_search_by_title_keyword(self, mock_database_context):
        service = _make_service()
        problem = _make_problem(1000, "A+B")
        service.problem_repository.find_by_id_prefix.return_value = []
        service.problem_repository.find_by_title_keyword.return_value = [problem]
        service.target_repository.find_all_active.return_value = []
        service.tag_repository.find_by_ids_and_active.return_value = []
        service.tier_repository.find_by_levels.return_value = []

        result = await service.search_problem_by_keyword("A+B")

        assert len(result[1]) == 1  # title-based results
        assert result[1][0].problem_title == "A+B"


class TestGetProblemsInfo:
    """get_problems_info() 이벤트 핸들러 테스트"""

    async def test_get_problems_info_empty(self, mock_database_context):
        service = _make_service()
        service.problem_repository.find_by_ids.return_value = []

        from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
        payload = GetProblemsInfoPayload(problem_ids=[])

        result = await service.get_problems_info(payload)

        assert result.problems == {}

    async def test_get_problems_info_with_data(self, mock_database_context):
        service = _make_service()
        problem = _make_problem(1000, "A+B", tier_level=5)
        service.problem_repository.find_by_ids.return_value = [problem]
        service.target_repository.find_all_active.return_value = []
        service.tag_repository.find_by_ids_and_active.return_value = []

        tier_mock = MagicMock()
        tier_mock.tier_level = 5
        tier_mock.tier_code = "Silver V"
        service.tier_repository.find_by_levels.return_value = [tier_mock]

        from app.baekjoon.domain.event.get_problems_info_payload import GetProblemsInfoPayload
        payload = GetProblemsInfoPayload(problem_ids=[1000])

        result = await service.get_problems_info(payload)

        assert 1000 in result.problems
        assert result.problems[1000].problem_title == "A+B"
        assert result.problems[1000].problem_tier_name == "Silver V"


class TestGetProblemsInfoLogic:
    """_get_problems_info_logic() 내부 로직 테스트"""

    async def test_empty_problems_returns_empty(self, mock_database_context):
        service = _make_service()

        result = await service._get_problems_info_logic([])

        assert result.problems == {}

    async def test_problem_with_tags_and_targets(self, mock_database_context):
        service = _make_service()

        # Problem with a tag
        problem = _make_problem(1000, "A+B", tier_level=5)
        tag_ref = MagicMock()
        tag_ref.tag_id = TagId(1)
        problem.tags = [tag_ref]

        tag = _make_tag(1, "dp")
        service.tag_repository.find_by_ids_and_active.return_value = [tag]

        target = _make_target(1, "COTE")
        target_tag = MagicMock()
        target_tag.tag_id = TagId(1)
        target.required_tags = [target_tag]
        service.target_repository.find_all_active.return_value = [target]

        tier_mock = MagicMock()
        tier_mock.tier_level = 5
        tier_mock.tier_code = "Silver V"
        service.tier_repository.find_by_levels.return_value = [tier_mock]

        result = await service._get_problems_info_logic([problem])

        assert 1000 in result.problems
        problem_info = result.problems[1000]
        assert len(problem_info.tags) == 1
        assert problem_info.tags[0].tag_code == "dp"
        assert len(problem_info.tags[0].tag_targets) == 1
        assert problem_info.tags[0].tag_targets[0].target_code == "COTE"
