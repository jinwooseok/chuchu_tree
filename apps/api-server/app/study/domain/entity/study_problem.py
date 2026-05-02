from dataclasses import dataclass, field
from datetime import date, datetime

from app.common.domain.vo.identifiers import (
    ProblemId,
    StudyId,
    StudyProblemId,
    StudyProblemMemberId,
    UserAccountId,
)


@dataclass
class StudyProblemMember:
    study_problem_member_id: StudyProblemMemberId | None
    study_problem_id: StudyProblemId | None
    user_account_id: UserAccountId
    target_date: date
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None

    @classmethod
    def create(
        cls,
        study_problem_id: StudyProblemId | None,
        user_account_id: UserAccountId,
        target_date: date,
    ) -> "StudyProblemMember":
        now = datetime.now()
        return cls(
            study_problem_member_id=None,
            study_problem_id=study_problem_id,
            user_account_id=user_account_id,
            target_date=target_date,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )


@dataclass
class StudyProblem:
    study_problem_id: StudyProblemId | None
    study_id: StudyId
    problem_id: ProblemId
    assigned_by_user_account_id: UserAccountId
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    members: list[StudyProblemMember] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        study_id: StudyId,
        problem_id: ProblemId,
        assigned_by_user_account_id: UserAccountId,
    ) -> "StudyProblem":
        now = datetime.now()
        return cls(
            study_problem_id=None,
            study_id=study_id,
            problem_id=problem_id,
            assigned_by_user_account_id=assigned_by_user_account_id,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            members=[],
        )
