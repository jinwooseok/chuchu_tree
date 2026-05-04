import pytest
from datetime import datetime

from app.common.domain.enums import ExcludedReason, TagLevel
from app.common.domain.vo.identifiers import TagId
from app.tag.domain.entity.tag import Tag
from app.tag.domain.vo.tag_exclusion import TagExclusion


class TestTagCreate:
    """Tag.create() 팩토리 메서드 테스트"""

    def test_create_tag(self):
        tag = Tag.create(code="dp", level=TagLevel.REQUIREMENT)

        assert tag.tag_id is None
        assert tag.code == "dp"
        assert tag.level == TagLevel.REQUIREMENT
        assert tag.exclusion.excluded is False
        assert tag.problem_count == 0
        assert tag.aliases == []
        assert tag.deleted_at is None


class TestTagExclusion:
    """Tag.exclude() / include() 테스트"""

    def _make_tag(self) -> Tag:
        return Tag.create(code="dp", level=TagLevel.REQUIREMENT)

    def test_exclude_tag(self):
        tag = self._make_tag()
        tag.exclude(ExcludedReason.INSIGNIFICANT)

        assert tag.exclusion.excluded is True
        assert tag.exclusion.reason == ExcludedReason.INSIGNIFICANT

    def test_include_tag(self):
        tag = self._make_tag()
        tag.exclude(ExcludedReason.INSIGNIFICANT)
        tag.include()

        assert tag.exclusion.excluded is False
        assert tag.exclusion.reason is None


class TestTagParentRelation:
    """Tag.add_parent_tag() 테스트"""

    def test_add_parent_tag(self):
        tag = Tag.create(code="dp", level=TagLevel.REQUIREMENT)
        tag.tag_id = TagId(1)

        tag.add_parent_tag(TagId(2))

        assert len(tag.parent_tag_relations) == 1

    def test_add_self_as_parent_raises(self):
        tag = Tag.create(code="dp", level=TagLevel.REQUIREMENT)
        tag.tag_id = TagId(1)

        with pytest.raises(ValueError, match="Cannot add self as sub-tag"):
            tag.add_parent_tag(TagId(1))


class TestTagAlias:
    """Tag.add_alias() 테스트"""

    def _make_tag(self) -> Tag:
        return Tag.create(code="dp", level=TagLevel.REQUIREMENT)

    def test_add_alias(self):
        tag = self._make_tag()
        tag.add_alias("dynamic_programming")

        assert "dynamic_programming" in tag.aliases

    def test_add_duplicate_alias_is_idempotent(self):
        tag = self._make_tag()
        tag.add_alias("dp")
        tag.add_alias("dp")

        assert tag.aliases.count("dp") == 1


class TestTagProblemCount:
    """Tag.increment_problem_count() 테스트"""

    def test_increment(self):
        tag = Tag.create(code="dp", level=TagLevel.REQUIREMENT)
        tag.increment_problem_count()

        assert tag.problem_count == 1

    def test_multiple_increments(self):
        tag = Tag.create(code="dp", level=TagLevel.REQUIREMENT)
        for _ in range(5):
            tag.increment_problem_count()

        assert tag.problem_count == 5
