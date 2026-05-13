from pydantic import BaseModel

from app.study.application.query.study_recommend_query import StudyRecommendedProblemQuery


class NoticeRequestedPayload(BaseModel):
    recipient_user_account_id: int
    category: str
    category_detail: str
    content: dict


class StudyRecommendationCompletedPayload(BaseModel):
    study_id: int
    requester_user_account_id: int
    problems: list[StudyRecommendedProblemQuery]


class StudyProblemAssignedPayload(BaseModel):
    study_id: int
    target_date: str
    study_problem_id: int
    problem_id: int
    problem_title: str
    problem_tier_level: int
    problem_tier_name: str
    problem_class_level: int | None
    tags: list[dict]
    representative_tag: dict | None
    assignees: list[dict]
    assigner_user_account_id: int
