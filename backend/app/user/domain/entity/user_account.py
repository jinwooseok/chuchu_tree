from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

from app.core.error_codes import ErrorCode
from app.core.exception import APIException

class Provider(str, Enum):
    KAKAO = "KAKAO"
    NAVER = "NAVER"
    GOOGLE = "GOOGLE"
    NONE = "NONE"


@dataclass(frozen=True)
class UserAccountId:
    """VO"""
    value: int
    
    def __post_init__(self):
        if self.value <= 0:
            raise ValueError("UserAccountId must be positive")

@dataclass
class UserAccount:
    """Aggregate Root - 유저 계정"""
    user_account_id: UserAccountId|None
    provider: Provider
    provider_id: str|None
    registered_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    account_links: list['AccountLink'] = field(default_factory=list)
    targets: list['UserTarget'] = field(default_factory=list)
    
    @staticmethod
    def create(provider: Provider, provider_id: str|None) -> 'UserAccount':
        """팩토리 메서드 - 새 유저 생성"""
        now = datetime.now()
        return UserAccount(
            user_account_id=None,  # DB에서 할당
            provider=provider,
            provider_id=provider_id,
            registered_at=now,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            account_links=[],
            targets=[]
        )
    
    def link_baekjoon_account(self, bj_account_id: 'BaekjoonAccountId') -> None:
        """도메인 로직 - 백준 계정 연동"""
        if self._is_already_linked(bj_account_id):
            raise APIException(ErrorCode.IS_ALREADY_LINKED)
        
        self.account_links.append(
            AccountLink.create(self.user_account_id, bj_account_id)
        )
        self.updated_at = datetime.now()
        
    def unlink_baekjoon_account(self, bj_account_id: 'BaekjoonAccountId') -> None:
        """도메인 로직 - 백준 계정 연동 해제"""
        self.account_links = [
            link for link in self.account_links
            if link.bj_account_id.value != bj_account_id.value or link.deleted_at is not None
        ]
        self.updated_at = datetime.now()
        
    def set_target(self, target_id: 'TargetId') -> None:
        """도메인 로직 - 목표 설정"""
        if self._has_target(target_id):
            raise ValueError(f"이미 설정된 목표입니다: {target_id.value}")
        
        self.targets.append(UserTarget.create(self.user_account_id, target_id))
        self.updated_at = datetime.now()
        
    def remove_target(self, target_id: 'TargetId') -> None:
        """도메인 로직 - 목표 제거"""
        for target in self.targets:
            if target.target_id.value == target_id.value:
                target.mark_as_deleted()
        self.updated_at = datetime.now()
    
    def _is_already_linked(self, bj_account_id: 'BaekjoonAccountId') -> bool:
        return any(
            link.bj_account_id.value == bj_account_id.value and link.deleted_at is None
            for link in self.account_links
        )
    
    def _has_target(self, target_id: 'TargetId') -> bool:
        return any(
            t.target_id.value == target_id.value and t.deleted_at is None
            for t in self.targets
        )