from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.recommendation.presentation.schema.response.recommendation_response import (
    RecommendReason,
    TagInfo,
)
from app.study.application.query.study_recommend_query import (
    StudyMemberSolveInfoQuery,
    StudyRecommendedProblemQuery,
    StudyRecommendProblemsQuery,
)


class StudyMemberSolveInfoResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_account_id: int
    bj_account_id: str
    solved: bool

    @classmethod
    def from_query(cls, q: StudyMemberSolveInfoQuery) -> "StudyMemberSolveInfoResponse":
        return cls(
            user_account_id=q.user_account_id,
            bj_account_id=q.bj_account_id,
            solved=q.solved,
        )


class StudyRecommendedProblemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    problem_id: int
    problem_title: str
    problem_tier_level: int
    problem_tier_name: str
    problem_class_level: int
    # "recommand" 오타 유지 (기존 추천 API와 alias 일치)
    recommand_reasons: list[RecommendReason]
    tags: list[TagInfo]
    study_member_solve_info: list[StudyMemberSolveInfoResponse]

    @classmethod
    def from_query(cls, q: StudyRecommendedProblemQuery) -> "StudyRecommendedProblemResponse":
        return cls(
            problem_id=q.problem_id,
            problem_title=q.problem_title,
            problem_tier_level=q.problem_tier_level,
            problem_tier_name=q.problem_tier_name,
            problem_class_level=q.problem_class_level,
            recommand_reasons=[RecommendReason.from_query(r) for r in q.recommend_reasons],
            tags=[TagInfo.from_query(t) for t in q.tags],
            study_member_solve_info=[StudyMemberSolveInfoResponse.from_query(i) for i in q.study_member_solve_info],
        )


class StudyRecommendationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    problems: list[StudyRecommendedProblemResponse]

    @classmethod
    def from_query(cls, q: StudyRecommendProblemsQuery) -> "StudyRecommendationResponse":
        return cls(problems=[StudyRecommendedProblemResponse.from_query(p) for p in q.problems])
