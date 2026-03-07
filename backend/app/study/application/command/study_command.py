from dataclasses import dataclass, field


@dataclass
class SearchUserCommand:
    keyword: str
    limit: int = 5


@dataclass
class CreateStudyCommand:
    requester_user_account_id: int
    study_name: str
    description: str | None
    max_members: int
    invitee_user_account_ids: list[int] = field(default_factory=list)


@dataclass
class GetStudyDetailCommand:
    study_id: int
    requester_user_account_id: int


@dataclass
class SearchStudyCommand:
    keyword: str
    limit: int = 5


@dataclass
class UpdateStudyCommand:
    study_id: int
    requester_user_account_id: int
    description: str | None = None
    max_members: int | None = None


@dataclass
class DeleteStudyCommand:
    study_id: int
    requester_user_account_id: int


@dataclass
class GetMyStudiesCommand:
    requester_user_account_id: int


@dataclass
class ValidateStudyNameCommand:
    name: str


@dataclass
class LeaveStudyCommand:
    study_id: int
    requester_user_account_id: int


@dataclass
class KickStudyMemberCommand:
    study_id: int
    requester_user_account_id: int
    target_user_account_id: int


@dataclass
class SendStudyInvitationCommand:
    study_id: int
    requester_user_account_id: int
    invitee_user_account_id: int


@dataclass
class CancelStudyInvitationCommand:
    study_id: int
    invitation_id: int
    requester_user_account_id: int


@dataclass
class GetMyInvitationsCommand:
    requester_user_account_id: int


@dataclass
class GetStudyInvitationsCommand:
    study_id: int
    requester_user_account_id: int


@dataclass
class AcceptStudyInvitationCommand:
    invitation_id: int
    requester_user_account_id: int


@dataclass
class RejectStudyInvitationCommand:
    invitation_id: int
    requester_user_account_id: int


@dataclass
class ApplyToStudyCommand:
    study_id: int
    requester_user_account_id: int
    message: str | None = None


@dataclass
class CancelStudyApplicationCommand:
    study_id: int
    requester_user_account_id: int


@dataclass
class GetStudyApplicationsCommand:
    study_id: int
    requester_user_account_id: int


@dataclass
class AcceptStudyApplicationCommand:
    application_id: int
    requester_user_account_id: int


@dataclass
class RejectStudyApplicationCommand:
    application_id: int
    requester_user_account_id: int


@dataclass
class MemberAssignment:
    user_account_id: int
    target_date: str  # "YYYY-MM-DD"


@dataclass
class AssignStudyProblemAllCommand:
    study_id: int
    problem_id: int
    target_date: str  # ISO 8601
    requester_user_account_id: int


@dataclass
class AssignStudyProblemCommand:
    study_id: int
    problem_id: int
    assignments: list[MemberAssignment]
    requester_user_account_id: int


@dataclass
class DeleteStudyProblemCommand:
    study_id: int
    study_problem_id: int
    requester_user_account_id: int


@dataclass
class GetStudyProblemsCommand:
    study_id: int
    requester_user_account_id: int
    year: int
    month: int


@dataclass
class GetMyNoticesCommand:
    requester_user_account_id: int


@dataclass
class MarkNoticesReadCommand:
    notice_ids: list[int]
    requester_user_account_id: int


@dataclass
class RecommendStudyProblemsCommand:
    study_id: int
    requester_user_account_id: int
    target_user_account_id: int | None = None
    level_filter_codes: list | None = None
    tag_filter_codes: list | None = None
    exclusion_mode: str = "LENIENT"
    recommend_all_unsolved: bool = False
    count: int = 3
