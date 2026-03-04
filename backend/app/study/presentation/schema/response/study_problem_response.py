from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.study.application.query.study_problem_query import (
    MemberSolveInfoQuery,
    StudyDayDataQuery,
    StudyProblemItemQuery,
    StudyProblemsQuery,
)


class MemberSolveInfoResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_account_id: int
    bj_account_id: str
    user_code: str
    solved: bool
    solve_date: str | None

    @classmethod
    def from_query(cls, q: MemberSolveInfoQuery) -> "MemberSolveInfoResponse":
        return cls(
            user_account_id=q.user_account_id,
            bj_account_id=q.bj_account_id,
            user_code=q.user_code,
            solved=q.solved,
            solve_date=q.solve_date,
        )


class StudyProblemItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    study_problem_id: int
    problem_id: int
    title: str
    tier: int
    solve_info: list[MemberSolveInfoResponse]
    status: str

    @classmethod
    def from_query(cls, q: StudyProblemItemQuery) -> "StudyProblemItemResponse":
        return cls(
            study_problem_id=q.study_problem_id,
            problem_id=q.problem_id,
            title=q.title,
            tier=q.tier,
            solve_info=[MemberSolveInfoResponse.from_query(m) for m in q.solve_info],
            status=q.status,
        )


class StudyDayDataResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    target_date: str
    problems: list[StudyProblemItemResponse]

    @classmethod
    def from_query(cls, q: StudyDayDataQuery) -> "StudyDayDataResponse":
        return cls(
            target_date=q.target_date,
            problems=[StudyProblemItemResponse.from_query(p) for p in q.problems],
        )


class StudyProblemsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    items: list[StudyDayDataResponse]

    @classmethod
    def from_query(cls, q: StudyProblemsQuery) -> "StudyProblemsResponse":
        return cls(items=[StudyDayDataResponse.from_query(d) for d in q.items])
