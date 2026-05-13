from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.baekjoon.presentation.schema.response.get_monthly_problems_response import (
    RepresentativeTagSummaryResponse,
    TagInfoResponse,
)
from app.study.domain.event.payloads import StudyProblemAssignedPayload


class StudyProblemAssignedSSEResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    target_date: str
    study_problem_id: int
    problem_id: int
    problem_title: str
    problem_tier_level: int
    problem_tier_name: str
    problem_class_level: int | None
    tags: list[TagInfoResponse]
    representative_tag: RepresentativeTagSummaryResponse | None = None
    solve_info: list = []

    @classmethod
    def from_payload(cls, payload: StudyProblemAssignedPayload) -> "StudyProblemAssignedSSEResponse":
        return cls(
            target_date=payload.target_date,
            study_problem_id=payload.study_problem_id,
            problem_id=payload.problem_id,
            problem_title=payload.problem_title,
            problem_tier_level=payload.problem_tier_level,
            problem_tier_name=payload.problem_tier_name,
            problem_class_level=payload.problem_class_level,
            tags=[TagInfoResponse(**t) for t in payload.tags],
            representative_tag=None,
            solve_info=[],
        )
