"""사용자 도메인 서비스 결과 Value Objects"""

from dataclasses import dataclass

from app.user.domain.entity.user_account import UserAccount


@dataclass(frozen=True)
class FindOrCreateUserResult:
    """사용자 조회/생성 결과"""

    user_account: UserAccount
    is_new_user: bool

    @property
    def user_account_id(self) -> int:
        """편의 메서드: user_account_id 직접 접근"""
        return self.user_account.user_account_id


@dataclass(frozen=True)
class UpdateUserProfileResult:
    """사용자 프로필 업데이트 결과"""

    user_account: UserAccount
    updated_fields: list[str]  # 업데이트된 필드명 리스트

    @property
    def has_updates(self) -> bool:
        """변경사항이 있는지 확인"""
        return len(self.updated_fields) > 0
