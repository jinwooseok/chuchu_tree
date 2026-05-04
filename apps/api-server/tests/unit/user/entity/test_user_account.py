import pytest
from datetime import datetime, timedelta

from app.common.domain.enums import Provider
from app.common.domain.vo.identifiers import (
    UserAccountId, BaekjoonAccountId, TargetId
)
from app.core.exception import APIException
from app.user.domain.entity.user_account import UserAccount
from app.user.domain.entity.account_link import AccountLink


class TestUserAccountCreate:
    """UserAccount.create() 팩토리 메서드 테스트"""

    def test_create_user_account(self):
        user = UserAccount.create(
            provider=Provider.KAKAO,
            provider_id="kakao_123",
            email="test@example.com"
        )

        assert user.user_account_id is None
        assert user.provider == Provider.KAKAO
        assert user.provider_id == "kakao_123"
        assert user.email == "test@example.com"
        assert user.profile_image is None
        assert user.deleted_at is None
        assert user.account_links == []
        assert user.targets == []

    def test_create_user_account_without_email(self):
        user = UserAccount.create(
            provider=Provider.GITHUB,
            provider_id="github_456"
        )

        assert user.email is None
        assert user.provider == Provider.GITHUB


class TestUserAccountLinkBaekjoon:
    """UserAccount.link_baekjoon_account() 테스트"""

    def _make_user(self, user_id: int = 1) -> UserAccount:
        now = datetime.now()
        return UserAccount(
            user_account_id=UserAccountId(user_id),
            provider=Provider.KAKAO,
            provider_id="kakao_123",
            email="test@example.com",
            profile_image=None,
            registered_at=now,
            created_at=now,
            updated_at=now,
            account_links=[],
            targets=[]
        )

    def test_link_baekjoon_account_first_time(self):
        user = self._make_user()
        bj_id = BaekjoonAccountId("test_bj")

        user.link_baekjoon_account(bj_id)

        assert len(user.account_links) == 1
        assert user.account_links[0].bj_account_id == bj_id
        assert user.account_links[0].deleted_at is None

    def test_link_already_linked_account_raises(self):
        user = self._make_user()
        bj_id = BaekjoonAccountId("test_bj")
        user.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=bj_id,
                created_at=datetime.now() - timedelta(days=10),
                deleted_at=None,
            )
        )

        with pytest.raises(APIException) as exc_info:
            user.link_baekjoon_account(bj_id)

        assert exc_info.value.error_code == "IS_ALREALY_LINKED"

    def test_link_within_cooldown_period_raises(self):
        user = self._make_user()
        old_bj_id = BaekjoonAccountId("old_bj")
        user.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=old_bj_id,
                created_at=datetime.now() - timedelta(days=3),
                deleted_at=datetime.now() - timedelta(days=2),
            )
        )

        new_bj_id = BaekjoonAccountId("new_bj")

        with pytest.raises(APIException) as exc_info:
            user.link_baekjoon_account(new_bj_id)

        assert exc_info.value.error_code == "LINK_COOLDOWN_PERIOD"

    def test_link_after_cooldown_period_succeeds(self):
        user = self._make_user()
        old_bj_id = BaekjoonAccountId("old_bj")
        user.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=old_bj_id,
                created_at=datetime.now() - timedelta(days=10),
                deleted_at=datetime.now() - timedelta(days=9),
            )
        )

        new_bj_id = BaekjoonAccountId("new_bj")
        user.link_baekjoon_account(new_bj_id)

        assert len(user.account_links) == 2
        active_links = [l for l in user.account_links if l.deleted_at is None]
        assert len(active_links) == 1
        assert active_links[0].bj_account_id == new_bj_id

    def test_link_with_problems_sets_is_synced_false(self):
        user = self._make_user()
        bj_id = BaekjoonAccountId("test_bj")

        user.link_baekjoon_account(bj_id, problem_count=10)

        assert user.account_links[-1].is_synced is False

    def test_link_without_problems_sets_is_synced_true(self):
        user = self._make_user()
        bj_id = BaekjoonAccountId("test_bj")

        user.link_baekjoon_account(bj_id, problem_count=0)

        assert user.account_links[-1].is_synced is True

    def test_link_default_problem_count_sets_is_synced_true(self):
        """problem_count 미전달 시 기본값 0이므로 is_synced=True"""
        user = self._make_user()
        bj_id = BaekjoonAccountId("test_bj")

        user.link_baekjoon_account(bj_id)

        assert user.account_links[-1].is_synced is True

    def test_link_deactivates_existing_active_link(self):
        user = self._make_user()
        old_bj_id = BaekjoonAccountId("old_bj")
        user.account_links.append(
            AccountLink(
                account_link_id=None,
                user_account_id=UserAccountId(1),
                bj_account_id=old_bj_id,
                created_at=datetime.now() - timedelta(days=10),
                deleted_at=None,
            )
        )

        new_bj_id = BaekjoonAccountId("new_bj")
        user.link_baekjoon_account(new_bj_id)

        old_link = user.account_links[0]
        assert old_link.deleted_at is not None


class TestUserAccountUnlinkBaekjoon:
    """UserAccount.unlink_baekjoon_account() 테스트"""

    def test_unlink_removes_active_link(self):
        now = datetime.now()
        user = UserAccount(
            user_account_id=UserAccountId(1),
            provider=Provider.KAKAO,
            provider_id="kakao_123",
            email=None,
            profile_image=None,
            registered_at=now,
            created_at=now,
            updated_at=now,
            account_links=[
                AccountLink(
                    account_link_id=None,
                    user_account_id=UserAccountId(1),
                    bj_account_id=BaekjoonAccountId("test_bj"),
                    created_at=now,
                    deleted_at=None,
                )
            ],
            targets=[]
        )

        user.unlink_baekjoon_account(BaekjoonAccountId("test_bj"))

        active_links = [l for l in user.account_links if l.deleted_at is None]
        assert len(active_links) == 0


class TestUserAccountTarget:
    """UserAccount.set_target() / remove_target() 테스트"""

    def _make_user(self) -> UserAccount:
        now = datetime.now()
        return UserAccount(
            user_account_id=UserAccountId(1),
            provider=Provider.KAKAO,
            provider_id="kakao_123",
            email=None,
            profile_image=None,
            registered_at=now,
            created_at=now,
            updated_at=now,
            account_links=[],
            targets=[]
        )

    def test_set_target_first_time(self):
        user = self._make_user()
        user.set_target(TargetId(1))

        assert len(user.targets) == 1
        assert user.targets[0].target_id == TargetId(1)
        assert user.targets[0].deleted_at is None

    def test_set_same_target_is_idempotent(self):
        user = self._make_user()
        user.set_target(TargetId(1))
        user.set_target(TargetId(1))

        active_targets = [t for t in user.targets if t.deleted_at is None]
        assert len(active_targets) == 1

    def test_set_different_target_deactivates_old(self):
        user = self._make_user()
        user.set_target(TargetId(1))
        user.set_target(TargetId(2))

        active_targets = [t for t in user.targets if t.deleted_at is None]
        assert len(active_targets) == 1
        assert active_targets[0].target_id == TargetId(2)

    def test_remove_target(self):
        user = self._make_user()
        user.set_target(TargetId(1))
        user.remove_target(TargetId(1))

        active_targets = [t for t in user.targets if t.deleted_at is None]
        assert len(active_targets) == 0


class TestUserAccountProfileImage:
    """UserAccount.update_profile_image() 테스트"""

    def test_update_profile_image(self):
        user = UserAccount.create(Provider.KAKAO, "kakao_123")
        user.update_profile_image("https://example.com/img.jpg")

        assert user.profile_image == "https://example.com/img.jpg"
