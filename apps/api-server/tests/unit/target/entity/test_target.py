import pytest
from datetime import datetime

from app.common.domain.vo.identifiers import TagId, TargetId
from app.core.exception import APIException
from app.target.domain.entity.target import Target


class TestTargetCreate:
    """Target.create() 팩토리 메서드 테스트"""

    def test_create_target(self):
        target = Target.create(code="COTE", display_name="코딩테스트 준비")

        assert target.target_id is None
        assert target.code == "COTE"
        assert target.display_name == "코딩테스트 준비"
        assert target.active is True
        assert target.required_tags == []
        assert target.deleted_at is None


class TestTargetRequiredTag:
    """Target.add_required_tag() / remove_required_tag() 테스트"""

    def _make_target(self) -> Target:
        target = Target.create(code="COTE", display_name="코딩테스트 준비")
        target.target_id = TargetId(1)
        return target

    def test_add_required_tag(self):
        target = self._make_target()
        target.add_required_tag(TagId(1))

        assert len(target.required_tags) == 1
        assert target.required_tags[0].tag_id == TagId(1)

    def test_add_duplicate_required_tag_raises(self):
        target = self._make_target()
        target.add_required_tag(TagId(1))

        with pytest.raises(APIException):
            target.add_required_tag(TagId(1))

    def test_remove_required_tag(self):
        target = self._make_target()
        target.add_required_tag(TagId(1))
        target.remove_required_tag(TagId(1))

        active = target.get_active_tags()
        assert len(active) == 0

    def test_remove_nonexistent_tag_raises(self):
        target = self._make_target()

        with pytest.raises(APIException):
            target.remove_required_tag(TagId(999))

    def test_get_active_tags(self):
        target = self._make_target()
        target.add_required_tag(TagId(1))
        target.add_required_tag(TagId(2))
        target.add_required_tag(TagId(3))
        target.remove_required_tag(TagId(2))

        active = target.get_active_tags()
        values = {t.value for t in active}
        assert values == {1, 3}


class TestTargetActivation:
    """Target.activate() / deactivate() 테스트"""

    def test_deactivate(self):
        target = Target.create(code="COTE", display_name="코테")
        target.deactivate()

        assert target.active is False

    def test_activate(self):
        target = Target.create(code="COTE", display_name="코테")
        target.deactivate()
        target.activate()

        assert target.active is True


class TestTargetDisplayName:
    """Target.update_display_name() 테스트"""

    def test_update_display_name(self):
        target = Target.create(code="COTE", display_name="코테")
        target.update_display_name("코딩테스트 준비")

        assert target.display_name == "코딩테스트 준비"

    def test_update_empty_name_raises(self):
        target = Target.create(code="COTE", display_name="코테")

        with pytest.raises(APIException):
            target.update_display_name("")

    def test_update_whitespace_name_raises(self):
        target = Target.create(code="COTE", display_name="코테")

        with pytest.raises(APIException):
            target.update_display_name("   ")
