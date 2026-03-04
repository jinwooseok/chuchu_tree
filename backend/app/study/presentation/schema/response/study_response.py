from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.study.application.query.study_query import (
    CreateStudyQuery,
    MyStudyItemQuery,
    NameAvailableQuery,
    StudyDetailQuery,
    StudyMemberQuery,
    StudyPendingApplicationQuery,
    StudyPendingInvitationQuery,
    StudySearchItemQuery,
)


class StudyMemberResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_account_id: int
    bj_account_id: str
    user_code: str
    role: str
    joined_at: str

    @classmethod
    def from_query(cls, q: StudyMemberQuery) -> "StudyMemberResponse":
        return cls(
            user_account_id=q.user_account_id,
            bj_account_id=q.bj_account_id,
            user_code=q.user_code,
            role=q.role,
            joined_at=q.joined_at,
        )


class StudyPendingInvitationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    invitation_id: int
    invitee_user_account_id: int
    invitee_bj_account_id: str
    invitee_user_code: str
    created_at: str

    @classmethod
    def from_query(cls, q: StudyPendingInvitationQuery) -> "StudyPendingInvitationResponse":
        return cls(
            invitation_id=q.invitation_id,
            invitee_user_account_id=q.invitee_user_account_id,
            invitee_bj_account_id=q.invitee_bj_account_id,
            invitee_user_code=q.invitee_user_code,
            created_at=q.created_at,
        )


class StudyPendingApplicationResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    application_id: int
    applicant_user_account_id: int
    applicant_bj_account_id: str
    applicant_user_code: str
    created_at: str

    @classmethod
    def from_query(cls, q: StudyPendingApplicationQuery) -> "StudyPendingApplicationResponse":
        return cls(
            application_id=q.application_id,
            applicant_user_account_id=q.applicant_user_account_id,
            applicant_bj_account_id=q.applicant_bj_account_id,
            applicant_user_code=q.applicant_user_code,
            created_at=q.created_at,
        )


class StudyDetailResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    study_id: int
    study_name: str
    owner_user_account_id: int
    description: str | None
    max_members: int
    member_count: int
    created_at: str
    members: list[StudyMemberResponse]
    pending_invitations: list[StudyPendingInvitationResponse]
    pending_applications: list[StudyPendingApplicationResponse]

    @classmethod
    def from_query(cls, q: StudyDetailQuery) -> "StudyDetailResponse":
        return cls(
            study_id=q.study_id,
            study_name=q.study_name,
            owner_user_account_id=q.owner_user_account_id,
            description=q.description,
            max_members=q.max_members,
            member_count=q.member_count,
            created_at=q.created_at,
            members=[StudyMemberResponse.from_query(m) for m in q.members],
            pending_invitations=[StudyPendingInvitationResponse.from_query(i) for i in q.pending_invitations],
            pending_applications=[StudyPendingApplicationResponse.from_query(a) for a in q.pending_applications],
        )


class CreateStudyResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    study_id: int
    study_name: str
    owner_user_account_id: int
    description: str | None
    max_members: int
    member_count: int
    created_at: str

    @classmethod
    def from_query(cls, q: CreateStudyQuery) -> "CreateStudyResponse":
        return cls(
            study_id=q.study_id,
            study_name=q.study_name,
            owner_user_account_id=q.owner_user_account_id,
            description=q.description,
            max_members=q.max_members,
            member_count=q.member_count,
            created_at=q.created_at,
        )


class StudySearchItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    study_id: int
    study_name: str
    owner_bj_account_id: str
    owner_user_code: str
    member_count: int

    @classmethod
    def from_query(cls, q: StudySearchItemQuery) -> "StudySearchItemResponse":
        return cls(
            study_id=q.study_id,
            study_name=q.study_name,
            owner_bj_account_id=q.owner_bj_account_id,
            owner_user_code=q.owner_user_code,
            member_count=q.member_count,
        )


class StudySearchResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    studies: list[StudySearchItemResponse]

    @classmethod
    def from_query(cls, queries: list[StudySearchItemQuery]) -> "StudySearchResponse":
        return cls(studies=[StudySearchItemResponse.from_query(q) for q in queries])


class MyStudyItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    study_id: int
    study_name: str
    owner_user_account_id: int
    owner_bj_account_id: str
    owner_user_code: str
    description: str | None
    max_members: int
    member_count: int
    created_at: str

    @classmethod
    def from_query(cls, q: MyStudyItemQuery) -> "MyStudyItemResponse":
        return cls(
            study_id=q.study_id,
            study_name=q.study_name,
            owner_user_account_id=q.owner_user_account_id,
            owner_bj_account_id=q.owner_bj_account_id,
            owner_user_code=q.owner_user_code,
            description=q.description,
            max_members=q.max_members,
            member_count=q.member_count,
            created_at=q.created_at,
        )


class MyStudiesResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    studies: list[MyStudyItemResponse]

    @classmethod
    def from_query(cls, queries: list[MyStudyItemQuery]) -> "MyStudiesResponse":
        return cls(studies=[MyStudyItemResponse.from_query(q) for q in queries])


class NameAvailableResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    available: bool

    @classmethod
    def from_query(cls, q: NameAvailableQuery) -> "NameAvailableResponse":
        return cls(available=q.available)
