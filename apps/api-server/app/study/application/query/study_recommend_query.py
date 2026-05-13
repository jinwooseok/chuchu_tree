from dataclasses import dataclass, field

from app.recommendation.application.query.recommend_problems_query import (
    RecommendReasonQuery,
    TagInfoQuery,
)


@dataclass
class StudyMemberSolveInfoQuery:
    user_account_id: int
    bj_account_id: str
    solved: bool


@dataclass
class StudyRecommendedProblemQuery:
    problem_id: int
    problem_title: str
    problem_tier_level: int
    problem_tier_name: str
    problem_class_level: int
    recommend_reasons: list[RecommendReasonQuery]
    tags: list[TagInfoQuery]
    study_member_solve_info: list[StudyMemberSolveInfoQuery] = field(default_factory=list)


@dataclass
class StudyRecommendProblemsQuery:
    problems: list[StudyRecommendedProblemQuery]
