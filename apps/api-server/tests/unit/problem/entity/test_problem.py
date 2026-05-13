import pytest
from datetime import datetime

from app.common.domain.vo.identifiers import ProblemId, TagId
from app.common.domain.vo.primitives import TierLevel
from app.core.exception import APIException
from app.problem.domain.entity.problem import Problem


class TestProblemCreate:
    """Problem.create() 팩토리 메서드 테스트"""

    def test_create_problem(self):
        problem = Problem.create(
            problem_id=ProblemId(1000),
            title="A+B",
            tier_level=TierLevel(1),
            solved_user_count=100000,
            class_level=1
        )

        assert problem.problem_id == ProblemId(1000)
        assert problem.title == "A+B"
        assert problem.tier_level == TierLevel(1)
        assert problem.solved_user_count == 100000
        assert problem.class_level == 1
        assert problem.tags == []
        assert problem.update_histories == []
        assert problem.deleted_at is None


class TestProblemTierUpdate:
    """Problem.update_tier_level() 테스트"""

    def _make_problem(self) -> Problem:
        return Problem.create(
            problem_id=ProblemId(1000),
            title="A+B",
            tier_level=TierLevel(1),
            solved_user_count=100000,
        )

    def test_update_tier_level(self):
        problem = self._make_problem()
        problem.update_tier_level(TierLevel(5))

        assert problem.tier_level == TierLevel(5)
        assert len(problem.update_histories) == 1

    def test_update_same_tier_is_noop(self):
        problem = self._make_problem()
        problem.update_tier_level(TierLevel(1))

        assert len(problem.update_histories) == 0


class TestProblemTitleUpdate:
    """Problem.update_title() 테스트"""

    def _make_problem(self) -> Problem:
        return Problem.create(
            problem_id=ProblemId(1000),
            title="A+B",
            tier_level=TierLevel(1),
            solved_user_count=100000,
        )

    def test_update_title(self):
        problem = self._make_problem()
        problem.update_title("A+B+C")

        assert problem.title == "A+B+C"
        assert len(problem.update_histories) == 1

    def test_update_same_title_is_noop(self):
        problem = self._make_problem()
        problem.update_title("A+B")

        assert len(problem.update_histories) == 0


class TestProblemTag:
    """Problem 태그 관련 테스트"""

    def _make_problem(self) -> Problem:
        return Problem.create(
            problem_id=ProblemId(1000),
            title="A+B",
            tier_level=TierLevel(1),
            solved_user_count=100000,
        )

    def test_add_tag(self):
        problem = self._make_problem()
        problem.add_tag(TagId(1))

        assert len(problem.tags) == 1

    def test_add_duplicate_tag_raises(self):
        problem = self._make_problem()
        problem.add_tag(TagId(1))

        with pytest.raises(APIException):
            problem.add_tag(TagId(1))

    def test_remove_tag(self):
        problem = self._make_problem()
        problem.add_tag(TagId(1))
        problem.remove_tag(TagId(1))

        assert len(problem.tags) == 0

    def test_has_any_tag_true(self):
        problem = self._make_problem()
        problem.add_tag(TagId(1))
        problem.add_tag(TagId(2))

        assert problem.has_any_tag([TagId(2), TagId(3)]) is True

    def test_has_any_tag_false(self):
        problem = self._make_problem()
        problem.add_tag(TagId(1))

        assert problem.has_any_tag([TagId(2), TagId(3)]) is False

    def test_has_any_tag_empty_list(self):
        problem = self._make_problem()
        problem.add_tag(TagId(1))

        assert problem.has_any_tag([]) is False
