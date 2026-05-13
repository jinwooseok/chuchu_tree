from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CreateStudyRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    study_name: str
    description: str | None = None
    max_members: int = 10
    invitee_user_account_ids: list[int] = []


class UpdateStudyRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    description: str | None = None
    max_members: int | None = None


class SendInvitationRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    invitee_user_account_id: int


class ApplyToStudyRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    message: str | None = None


class AssignStudyProblemAllRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    problem_id: int
    target_date: str  # "YYYY-MM-DD" — 전원 동일 날짜


class MemberAssignmentRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_account_id: int
    target_date: str  # "YYYY-MM-DD"


class AssignStudyProblemRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    problem_id: int
    assignments: list[MemberAssignmentRequest]


class MarkNoticesReadRequest(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    notice_ids: list[int]
