from dataclasses import dataclass, field

from app.problem.application.query.problems_info_query import TagInfoQuery


@dataclass
class MemberSolveInfoQuery:
    user_account_id: int
    bj_account_id: str
    user_code: str
    solved: bool
    solve_date: str | None  # solved이면 ISO string, 아니면 None


@dataclass
class StudyProblemItemQuery:
    study_problem_id: int
    problem_id: int
    problem_title: str
    problem_tier_level: int
    problem_tier_name: str
    problem_class_level: int | None
    tags: list[TagInfoQuery]
    solve_info: list[MemberSolveInfoQuery] = field(default_factory=list)


@dataclass
class StudyDayDataQuery:
    target_date: str
    problems: list[StudyProblemItemQuery] = field(default_factory=list)


@dataclass
class StudyProblemsQuery:
    study_data: list[StudyDayDataQuery] = field(default_factory=list)
