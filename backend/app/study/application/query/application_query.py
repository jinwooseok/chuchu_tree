from dataclasses import dataclass


@dataclass
class ApplicationQuery:
    application_id: int
    study_id: int
    applicant_user_account_id: int
    applicant_bj_account_id: str
    applicant_user_code: str
    status: str
    message: str | None
    created_at: str
