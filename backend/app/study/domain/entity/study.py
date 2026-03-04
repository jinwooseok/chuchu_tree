from dataclasses import dataclass, field
from datetime import datetime

from app.common.domain.enums import StudyMemberRole
from app.common.domain.vo.identifiers import StudyId, StudyMemberId, UserAccountId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.study.domain.entity.study_member import StudyMember


@dataclass
class Study:
    study_id: StudyId | None
    study_name: str
    owner_user_account_id: UserAccountId
    description: str | None
    max_members: int
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime | None = None
    members: list[StudyMember] = field(default_factory=list)

    @classmethod
    def create(
        cls,
        study_name: str,
        owner_user_account_id: UserAccountId,
        description: str | None,
        max_members: int,
    ) -> "Study":
        now = datetime.now()
        return cls(
            study_id=None,
            study_name=study_name,
            owner_user_account_id=owner_user_account_id,
            description=description,
            max_members=max_members,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            members=[],
        )

    def add_member(self, user_account_id: UserAccountId, role: StudyMemberRole = StudyMemberRole.MEMBER) -> StudyMember:
        if self.is_full():
            raise APIException(ErrorCode.STUDY_FULL)
        if self.is_member(user_account_id):
            raise APIException(ErrorCode.STUDY_ALREADY_MEMBER)
        now = datetime.now()
        member = StudyMember(
            study_member_id=None,
            study_id=self.study_id,
            user_account_id=user_account_id,
            role=role,
            joined_at=now,
            created_at=now,
            updated_at=now,
            deleted_at=None,
        )
        self.members.append(member)
        return member

    def remove_member(self, user_account_id: UserAccountId) -> None:
        for member in self.members:
            if member.user_account_id.value == user_account_id.value and member.deleted_at is None:
                member.deleted_at = datetime.now()
                return

    def is_member(self, user_account_id: UserAccountId) -> bool:
        return any(
            m.user_account_id.value == user_account_id.value and m.deleted_at is None
            for m in self.members
        )

    def is_owner(self, user_account_id: UserAccountId) -> bool:
        return self.owner_user_account_id.value == user_account_id.value

    def is_full(self) -> bool:
        return self.active_member_count() >= self.max_members

    def active_member_count(self) -> int:
        return sum(1 for m in self.members if m.deleted_at is None)

    def delegate_owner(self, to_user_account_id: int) -> None:
        for m in self.members:
            if m.user_account_id.value == to_user_account_id and m.deleted_at is None:
                m.role = StudyMemberRole.OWNER
                self.owner_user_account_id = m.user_account_id
                return
        raise APIException(ErrorCode.STUDY_NOT_MEMBER)
