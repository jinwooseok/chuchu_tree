import pytest
from datetime import date, datetime

from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.problem_banned_record import ProblemBannedRecord
from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.domain.entity.tag_customization import TagCustomization
from app.common.domain.enums import ExcludedReason
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId
from app.core.exception import APIException


class TestUserActivityCreate:
    """UserActivity.create() 팩토리 메서드 테스트"""

    def test_create_user_activity(self):
        ua = UserActivity.create(UserAccountId(1))

        assert ua.user_activity_id is None
        assert ua.user_account_id == UserAccountId(1)
        assert ua.will_solve_problems == []
        assert ua.banned_problems == []
        assert ua.solved_problems == []
        assert ua.tag_customizations == []


class TestUserActivityWillSolve:
    """풀 예정 문제 관련 테스트"""

    def _make_activity(self) -> UserActivity:
        return UserActivity.create(UserAccountId(1))

    def test_mark_problem_to_solve(self):
        ua = self._make_activity()
        ua.mark_problem_to_solve(ProblemId(1000))

        assert len(ua.will_solve_problems) == 1
        assert ua.will_solve_problems[0].problem_id == ProblemId(1000)

    def test_mark_banned_problem_raises(self):
        ua = self._make_activity()
        ua.ban_problem(ProblemId(1000))

        with pytest.raises(APIException):
            ua.mark_problem_to_solve(ProblemId(1000))

    def test_unmark_problem(self):
        ua = self._make_activity()
        ua.mark_problem_to_solve(ProblemId(1000))
        ua.unmark_problem(ProblemId(1000))

        active = [p for p in ua.will_solve_problems if p.deleted_at is None]
        assert len(active) == 0

    def test_mark_deleted_problem_restores(self):
        ua = self._make_activity()
        ua.mark_problem_to_solve(ProblemId(1000))
        ua.unmark_problem(ProblemId(1000))
        ua.mark_problem_to_solve(ProblemId(1000))

        active = [p for p in ua.will_solve_problems if p.deleted_at is None]
        assert len(active) == 1


class TestUserActivityBanProblem:
    """문제 차단 관련 테스트"""

    def _make_activity(self) -> UserActivity:
        return UserActivity.create(UserAccountId(1))

    def test_ban_problem(self):
        ua = self._make_activity()
        ua.ban_problem(ProblemId(1000))

        assert len(ua.banned_problems) == 1
        assert ua.banned_problems[0].problem_id == ProblemId(1000)

    def test_ban_already_banned_is_idempotent(self):
        ua = self._make_activity()
        ua.ban_problem(ProblemId(1000))
        ua.ban_problem(ProblemId(1000))

        assert len(ua.banned_problems) == 1

    def test_remove_ban(self):
        ua = self._make_activity()
        ua.ban_problem(ProblemId(1000))
        ua.remove_ban_problem(ProblemId(1000))

        active = [p for p in ua.banned_problems if p.deleted_at is None]
        assert len(active) == 0

    def test_remove_nonexistent_ban_does_nothing(self):
        ua = self._make_activity()
        ua.remove_ban_problem(ProblemId(9999))

        assert len(ua.banned_problems) == 0


class TestUserActivitySolvedProblem:
    """문제 해결 기록 관련 테스트"""

    def _make_activity(self) -> UserActivity:
        return UserActivity.create(UserAccountId(1))

    def test_record_problem_solved(self):
        ua = self._make_activity()
        ua.record_problem_solved(ProblemId(1000))

        assert len(ua.solved_problems) == 1
        assert ua.solved_problems[0].problem_id == ProblemId(1000)

    def test_record_already_solved_is_idempotent(self):
        ua = self._make_activity()
        ua.record_problem_solved(ProblemId(1000))
        ua.record_problem_solved(ProblemId(1000))

        assert len(ua.solved_problems) == 1

    def test_solving_removes_from_will_solve(self):
        ua = self._make_activity()
        ua.mark_problem_to_solve(ProblemId(1000))
        ua.record_problem_solved(ProblemId(1000))

        active_will_solve = [
            p for p in ua.will_solve_problems if p.deleted_at is None
        ]
        assert len(active_will_solve) == 0
        assert len(ua.solved_problems) == 1


class TestUserActivityTagCustomization:
    """태그 커스터마이징 관련 테스트"""

    def _make_activity(self) -> UserActivity:
        return UserActivity.create(UserAccountId(1))

    def test_customize_tag_exclude(self):
        ua = self._make_activity()
        ua.customize_tag(TagId(1), exclude=True, reason=ExcludedReason.INSIGNIFICANT)

        assert len(ua.tag_customizations) == 1
        assert ua.tag_customizations[0].excluded is True

    def test_update_existing_customization(self):
        ua = self._make_activity()
        ua.customize_tag(TagId(1), exclude=True, reason=ExcludedReason.INSIGNIFICANT)
        ua.customize_tag(TagId(1), exclude=False)

        assert len(ua.tag_customizations) == 1
        assert ua.tag_customizations[0].excluded is False

    def test_remove_tag_customization(self):
        ua = self._make_activity()
        ua.customize_tag(TagId(1), exclude=True)
        ua.remove_tag_customization(TagId(1))

        active = [tc for tc in ua.tag_customizations if tc.deleted_at is None]
        assert len(active) == 0

    def test_get_excluded_tag_ids(self):
        ua = self._make_activity()
        ua.customize_tag(TagId(1), exclude=True)
        ua.customize_tag(TagId(2), exclude=True)
        ua.customize_tag(TagId(3), exclude=False)

        excluded = ua.get_excluded_tag_ids()
        excluded_values = {t.value for t in excluded}

        assert excluded_values == {1, 2}


class TestUserActivityProperties:
    """Property 테스트 (solved_problem_ids, banned_problem_ids 등)"""

    def test_solved_problem_ids(self):
        ua = UserActivity.create(UserAccountId(1))
        ua.record_problem_solved(ProblemId(1000))
        ua.record_problem_solved(ProblemId(2000))

        ids = ua.solved_problem_ids
        assert ProblemId(1000) in ids
        assert ProblemId(2000) in ids
        assert len(ids) == 2

    def test_banned_problem_ids(self):
        ua = UserActivity.create(UserAccountId(1))
        ua.ban_problem(ProblemId(1000))

        ids = ua.banned_problem_ids
        assert ProblemId(1000) in ids
        assert len(ids) == 1

    def test_excluded_tag_ids_property(self):
        ua = UserActivity.create(UserAccountId(1))
        ua.customize_tag(TagId(1), exclude=True)
        ua.customize_tag(TagId(2), exclude=False)

        ids = ua.excluded_tag_ids
        assert TagId(1) in ids
        assert TagId(2) not in ids

    def test_will_solve_problem_ids(self):
        ua = UserActivity.create(UserAccountId(1))
        ua.mark_problem_to_solve(ProblemId(1000))

        ids = ua.will_solve_problem_ids
        assert ProblemId(1000) in ids
        assert len(ids) == 1
