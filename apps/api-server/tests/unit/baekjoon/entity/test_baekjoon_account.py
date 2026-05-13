import pytest
from datetime import date, datetime

from app.baekjoon.domain.entity.baekjoon_account import BaekjoonAccount
from app.common.domain.vo.identifiers import (
    BaekjoonAccountId, ProblemId, TagId, TagSkillId, TierId
)
from app.common.domain.vo.primitives import Rating, Statistics


class TestBaekjoonAccountCreate:
    """BaekjoonAccount.create() 팩토리 메서드 테스트"""

    def test_create_baekjoon_account(self):
        bj = BaekjoonAccount.create(
            bj_account_id=BaekjoonAccountId("test_user"),
            tier_id=TierId(10),
        )

        assert bj.bj_account_id == BaekjoonAccountId("test_user")
        assert bj.current_tier_id == TierId(10)
        assert bj.rating == Rating(0)
        assert bj.statistics == Statistics(0, 0, 0)
        assert bj.tier_histories == []
        assert bj.tag_skill_histories == []
        assert bj.problem_histories == []
        assert bj.streaks == []
        assert bj.deleted_at is None


class TestBaekjoonAccountTier:
    """티어 관련 도메인 로직 테스트"""

    def _make_account(self) -> BaekjoonAccount:
        return BaekjoonAccount.create(
            bj_account_id=BaekjoonAccountId("test_user"),
            tier_id=TierId(10),
        )

    def test_update_tier(self):
        bj = self._make_account()
        bj.update_tier(TierId(15))

        assert bj.current_tier_id == TierId(15)
        assert len(bj.tier_histories) == 1
        assert bj.tier_start_date == date.today()

    def test_update_same_tier_is_noop(self):
        bj = self._make_account()
        original_updated = bj.updated_at

        bj.update_tier(TierId(10))

        assert bj.current_tier_id == TierId(10)
        assert len(bj.tier_histories) == 0
        assert bj.updated_at == original_updated

    def test_multiple_tier_updates_create_history(self):
        bj = self._make_account()
        bj.update_tier(TierId(11))
        bj.update_tier(TierId(12))

        assert bj.current_tier_id == TierId(12)
        assert len(bj.tier_histories) == 2


class TestBaekjoonAccountStatistics:
    """통계 및 레이팅 테스트"""

    def _make_account(self) -> BaekjoonAccount:
        return BaekjoonAccount.create(
            bj_account_id=BaekjoonAccountId("test_user"),
            tier_id=TierId(10),
        )

    def test_update_statistics(self):
        bj = self._make_account()
        bj.update_statistics(
            contribution_count=100,
            class_level=3,
            longest_streak=50
        )

        assert bj.statistics.contribution_count == 100
        assert bj.statistics.class_level == 3
        assert bj.statistics.longest_streak == 50

    def test_update_rating(self):
        bj = self._make_account()
        bj.update_rating(1500)

        assert bj.rating == Rating(1500)


class TestBaekjoonAccountProblemHistory:
    """문제 해결 기록 테스트"""

    def _make_account(self) -> BaekjoonAccount:
        return BaekjoonAccount.create(
            bj_account_id=BaekjoonAccountId("test_user"),
            tier_id=TierId(10),
        )

    def test_record_problem_solved(self):
        bj = self._make_account()
        bj.record_problem_solved(ProblemId(1000))

        assert len(bj.problem_histories) == 1

    def test_record_problem_with_date(self):
        bj = self._make_account()
        bj.record_problem_solved(ProblemId(1000), solved_date=date(2025, 1, 15))

        assert len(bj.problem_histories) == 1

    def test_record_multiple_problems(self):
        bj = self._make_account()
        bj.record_problem_solved(ProblemId(1000))
        bj.record_problem_solved(ProblemId(2000))
        bj.record_problem_solved(ProblemId(3000))

        assert len(bj.problem_histories) == 3


class TestBaekjoonAccountStreak:
    """스트릭 관련 테스트"""

    def _make_account(self) -> BaekjoonAccount:
        return BaekjoonAccount.create(
            bj_account_id=BaekjoonAccountId("test_user"),
            tier_id=TierId(10),
        )

    def test_add_streak(self):
        bj = self._make_account()
        bj.add_streak(date(2025, 1, 15), solved_count=3)

        assert len(bj.streaks) == 1
        assert bj.streaks[0].solved_count == 3

    def test_add_or_update_streak_new(self):
        bj = self._make_account()
        bj.add_or_update_streak(date(2025, 1, 15), solved_count=3)

        assert len(bj.streaks) == 1
        assert bj.streaks[0].solved_count == 3

    def test_add_or_update_streak_existing(self):
        bj = self._make_account()
        bj.add_streak(date(2025, 1, 15), solved_count=3)
        bj.add_or_update_streak(date(2025, 1, 15), solved_count=5)

        assert len(bj.streaks) == 1
        assert bj.streaks[0].solved_count == 5


class TestBaekjoonAccountTagSkill:
    """태그 숙련도 테스트"""

    def test_update_tag_skill(self):
        bj = BaekjoonAccount.create(
            bj_account_id=BaekjoonAccountId("test_user"),
            tier_id=TierId(10),
        )
        bj.update_tag_skill(
            tag_id=TagId(1),
            new_skill_id=TagSkillId(2),
            prev_skill_id=TagSkillId(1)
        )

        assert len(bj.tag_skill_histories) == 1
