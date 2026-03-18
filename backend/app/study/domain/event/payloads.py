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
