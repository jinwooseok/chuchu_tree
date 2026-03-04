from dataclasses import dataclass, field


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
    title: str
    tier: int
    solve_info: list[MemberSolveInfoQuery] = field(default_factory=list)
    status: str = "will_solve"  # "solved" | "in_progress" | "will_solve"


@dataclass
class StudyDayDataQuery:
    target_date: str
    problems: list[StudyProblemItemQuery] = field(default_factory=list)


@dataclass
class StudyProblemsQuery:
    items: list[StudyDayDataQuery] = field(default_factory=list)
