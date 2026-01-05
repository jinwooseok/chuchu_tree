"""유저 태그 목록 조회 Query"""

from dataclasses import dataclass
from datetime import date

from app.common.domain.enums import SkillCode


@dataclass
class PrevTagQuery:
    """선수 태그 정보"""
    tag_id: int
    tag_code: str
    tag_display_name: str
    satisfied_yn: bool


@dataclass
class RequiredStatQuery:
    """태그 해금 요구사항"""
    required_min_tier: int
    prev_tags: list[PrevTagQuery]


@dataclass
class NextLevelStatQuery:
    """다음 레벨 요구사항"""
    next_level: str
    solved_problem_count: int
    required_min_tier: int
    higher_problem_tier: int


@dataclass
class AccountStatQuery:
    """유저의 태그별 통계"""
    current_level: str
    solved_problem_count: int
    required_min_tier: int | None
    higher_problem_tier: int | None
    last_solved_date: date | None


@dataclass
class TagAliasQuery:
    """태그 별칭"""
    alias: str


@dataclass
class TargetQuery:
    """목표 정보"""
    target_id: int
    target_code: str
    target_display_name: str


@dataclass
class UserTagDetailQuery:
    """유저 태그 상세 정보"""
    tag_id: int
    tag_code: str
    tag_display_name: str
    tag_targets: list[TargetQuery]
    tag_aliases: list[TagAliasQuery]
    required_stat: RequiredStatQuery | None
    next_level_stat: NextLevelStatQuery | None
    account_stat: AccountStatQuery
    locked_yn: bool
    excluded_yn: bool
    recommendation_yn: bool


@dataclass
class CategoryQuery:
    """태그 카테고리"""
    category_name: str
    tags: list[UserTagDetailQuery]


@dataclass
class UserTagsQuery:
    """유저 태그 목록 조회 결과"""
    categories: list[CategoryQuery]
    tags: list[UserTagDetailQuery]
