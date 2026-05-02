from dataclasses import dataclass


@dataclass
class MyApplicationQuery:
    application_id: int
    study_id: int
    study_name: str
    owner_user_account_id: int
    owner_bj_account_id: str
    owner_user_code: str
    status: str
    message: str | None
    created_at: str
    owner_profile_image_url: str | None = None


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
    applicant_profile_image_url: str | None = None
