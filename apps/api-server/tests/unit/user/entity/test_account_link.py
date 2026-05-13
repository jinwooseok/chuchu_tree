import pytest
from datetime import datetime

from app.common.domain.vo.identifiers import AccountLinkId, BaekjoonAccountId, UserAccountId
from app.user.domain.entity.account_link import AccountLink


class TestAccountLinkCreate:
    """AccountLink.create() 팩토리 메서드 테스트"""

    def test_create_default_is_synced_false(self):
        link = AccountLink.create(
            user_account_id=UserAccountId(1),
            bj_account_id=BaekjoonAccountId("test_bj")
        )

        assert link.is_synced is False
        assert link.account_link_id is None
        assert link.deleted_at is None

    def test_create_with_is_synced_true(self):
        link = AccountLink.create(
            user_account_id=UserAccountId(1),
            bj_account_id=BaekjoonAccountId("test_bj"),
            is_synced=True
        )

        assert link.is_synced is True

    def test_create_with_is_synced_false(self):
        link = AccountLink.create(
            user_account_id=UserAccountId(1),
            bj_account_id=BaekjoonAccountId("test_bj"),
            is_synced=False
        )

        assert link.is_synced is False


class TestAccountLinkMarkAsSynced:
    """AccountLink.mark_as_synced() 테스트"""

    def test_mark_as_synced(self):
        link = AccountLink.create(
            user_account_id=UserAccountId(1),
            bj_account_id=BaekjoonAccountId("test_bj")
        )
        assert link.is_synced is False

        link.mark_as_synced()

        assert link.is_synced is True

    def test_mark_as_synced_idempotent(self):
        link = AccountLink.create(
            user_account_id=UserAccountId(1),
            bj_account_id=BaekjoonAccountId("test_bj"),
            is_synced=True
        )

        link.mark_as_synced()

        assert link.is_synced is True


class TestAccountLinkMarkAsDeleted:
    """AccountLink.mark_as_deleted() 테스트"""

    def test_mark_as_deleted(self):
        link = AccountLink.create(
            user_account_id=UserAccountId(1),
            bj_account_id=BaekjoonAccountId("test_bj")
        )
        assert link.deleted_at is None

        link.mark_as_deleted()

        assert link.deleted_at is not None
