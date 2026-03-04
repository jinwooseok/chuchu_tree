from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.study.application.query.application_query import ApplicationQuery


class ApplicationItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    application_id: int
    study_id: int
    applicant_user_account_id: int
    applicant_bj_account_id: str
    applicant_user_code: str
    status: str
    message: str | None
    created_at: str

    @classmethod
    def from_query(cls, q: ApplicationQuery) -> "ApplicationItemResponse":
        return cls(
            application_id=q.application_id,
            study_id=q.study_id,
            applicant_user_account_id=q.applicant_user_account_id,
            applicant_bj_account_id=q.applicant_bj_account_id,
            applicant_user_code=q.applicant_user_code,
            status=q.status,
            message=q.message,
            created_at=q.created_at,
        )


class StudyApplicationsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    applications: list[ApplicationItemResponse]

    @classmethod
    def from_query(cls, queries: list[ApplicationQuery]) -> "StudyApplicationsResponse":
        return cls(applications=[ApplicationItemResponse.from_query(q) for q in queries])
