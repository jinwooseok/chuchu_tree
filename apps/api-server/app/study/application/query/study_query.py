from dataclasses import dataclass, field


@dataclass
class StudyMemberQuery:
    user_account_id: int
    bj_account_id: str
    user_code: str
    role: str
    joined_at: str
    profile_image_url: str | None = None


@dataclass
class StudyPendingInvitationQuery:
    invitation_id: int
    invitee_user_account_id: int
    invitee_bj_account_id: str
    invitee_user_code: str
    created_at: str
    profile_image_url: str | None = None


@dataclass
class StudyPendingApplicationQuery:
    application_id: int
    applicant_user_account_id: int
    applicant_bj_account_id: str
    applicant_user_code: str
    created_at: str
    profile_image_url: str | None = None


@dataclass
class StudyDetailQuery:
    study_id: int
    study_name: str
    owner_user_account_id: int
    description: str | None
    max_members: int
    member_count: int
    created_at: str
    members: list[StudyMemberQuery] = field(default_factory=list)
    pending_invitations: list[StudyPendingInvitationQuery] = field(default_factory=list)
    pending_applications: list[StudyPendingApplicationQuery] = field(default_factory=list)


@dataclass
class StudySearchItemQuery:
    study_id: int
    study_name: str
    owner_bj_account_id: str
    owner_user_code: str
    member_count: int
    owner_profile_image_url: str | None = None


@dataclass
class CreateStudyQuery:
    study_id: int
    study_name: str
    owner_user_account_id: int
    description: str | None
    max_members: int
    member_count: int
    created_at: str


@dataclass
class MyStudyItemQuery:
    study_id: int
    study_name: str
    owner_user_account_id: int
    owner_bj_account_id: str
    owner_user_code: str
    description: str | None
    max_members: int
    member_count: int
    created_at: str
    owner_profile_image_url: str | None = None


@dataclass
class NameAvailableQuery:
    available: bool
