from dataclasses import dataclass


@dataclass
class InvitationQuery:
    invitation_id: int
    study_id: int
    study_name: str
    inviter_user_account_id: int
    inviter_bj_account_id: str
    inviter_user_code: str
    status: str
    created_at: str
    inviter_profile_image_url: str | None = None
