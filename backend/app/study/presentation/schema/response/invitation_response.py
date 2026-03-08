from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.study.application.query.application_query import MyApplicationQuery
from app.study.application.query.invitation_query import InvitationQuery


class InvitationItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    invitation_id: int
    study_id: int
    study_name: str
    inviter_user_account_id: int
    inviter_bj_account_id: str
    inviter_user_code: str
    status: str
    created_at: str
    inviter_profile_image_url: str | None = None

    @classmethod
    def from_query(cls, q: InvitationQuery) -> "InvitationItemResponse":
        return cls(
            invitation_id=q.invitation_id,
            study_id=q.study_id,
            study_name=q.study_name,
            inviter_user_account_id=q.inviter_user_account_id,
            inviter_bj_account_id=q.inviter_bj_account_id,
            inviter_user_code=q.inviter_user_code,
            status=q.status,
            created_at=q.created_at,
            inviter_profile_image_url=q.inviter_profile_image_url,
        )


class MyInvitationsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    invitations: list[InvitationItemResponse]

    @classmethod
    def from_query(cls, queries: list[InvitationQuery]) -> "MyInvitationsResponse":
        return cls(invitations=[InvitationItemResponse.from_query(q) for q in queries])


class MyApplicationItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

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

    @classmethod
    def from_query(cls, q: MyApplicationQuery) -> "MyApplicationItemResponse":
        return cls(
            application_id=q.application_id,
            study_id=q.study_id,
            study_name=q.study_name,
            owner_user_account_id=q.owner_user_account_id,
            owner_bj_account_id=q.owner_bj_account_id,
            owner_user_code=q.owner_user_code,
            status=q.status,
            message=q.message,
            created_at=q.created_at,
            owner_profile_image_url=q.owner_profile_image_url,
        )


class MyPendingRequestsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    invitations: list[InvitationItemResponse]
    applications: list[MyApplicationItemResponse]

    @classmethod
    def from_queries(
        cls,
        invitation_queries: list[InvitationQuery],
        application_queries: list[MyApplicationQuery],
    ) -> "MyPendingRequestsResponse":
        return cls(
            invitations=[InvitationItemResponse.from_query(q) for q in invitation_queries],
            applications=[MyApplicationItemResponse.from_query(q) for q in application_queries],
        )
