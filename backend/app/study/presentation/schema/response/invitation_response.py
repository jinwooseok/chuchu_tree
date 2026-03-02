from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

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
        )


class MyInvitationsResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    invitations: list[InvitationItemResponse]

    @classmethod
    def from_query(cls, queries: list[InvitationQuery]) -> "MyInvitationsResponse":
        return cls(invitations=[InvitationItemResponse.from_query(q) for q in queries])
