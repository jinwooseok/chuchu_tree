from dataclasses import dataclass, field
from datetime import datetime, timedelta

from app.common.domain.vo.identifiers import BaekjoonAccountId, TargetId, UserAccountId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.user.domain.entity.account_link import AccountLink
from app.user.domain.entity.user_target import UserTarget
from app.common.domain.enums import Provider

@dataclass
class UserAccount:
    """Aggregate Root - 유저 계정"""
    user_account_id: UserAccountId|None
    provider: Provider
    provider_id: str|None
    profile_image: str|None
    registered_at: datetime
    created_at: datetime
    updated_at: datetime
    deleted_at: datetime|None = None
    account_links: list[AccountLink] = field(default_factory=list)
    targets: list[UserTarget] = field(default_factory=list)
    
    @staticmethod
    def create(provider: Provider, provider_id: str|None) -> 'UserAccount':
        now = datetime.now()
        return UserAccount(
            user_account_id=None,  # DB에서 할당
            provider=provider,
            profile_image=None,
            provider_id=provider_id,
            registered_at=now,
            created_at=now,
            updated_at=now,
            deleted_at=None,
            account_links=[],
            targets=[]
        )
    
    def link_baekjoon_account(self, bj_account_id: BaekjoonAccountId) -> None:
        """도메인 로직 - 백준 계정 연동"""
        now = datetime.now()
        
        # 1. 동일한 계정이 이미 '활성화' 상태인지 확인 (중복 연동 방지)
        active_link = next(
            (link for link in self.account_links 
             if link.bj_account_id.value == bj_account_id.value and link.deleted_at is None), 
            None
        )
        if active_link:
            raise APIException(ErrorCode.IS_ALREALY_LINKED)
        
        # 2. 7일 제한 정책 확인 (삭제된 이력 포함 가장 최근 연동 시도 시점 기준)
        if self.account_links:
            # 모든 링크(삭제된 것 포함) 중 가장 최근 생성일 찾기
            last_link_time = max(link.created_at for link in self.account_links)
            
            # 현재 시간과 비교 (7일이 경과했는지 확인)
            if datetime.now() < last_link_time + timedelta(days=7):
                # 남은 일수 계산 등을 에러 메시지에 포함할 수도 있습니다.
                raise APIException(ErrorCode.LINK_COOLDOWN_PERIOD)
        
        for link in self.account_links:
            if link.deleted_at is None:
                link.deleted_at = now
        
        # 4. 새로운 연동 정보 추가
        new_link = AccountLink.create(self.user_account_id, bj_account_id)
        self.account_links.append(new_link)
        
        self.updated_at = datetime.now()
        
    def unlink_baekjoon_account(self, bj_account_id: BaekjoonAccountId) -> None:
        """도메인 로직 - 백준 계정 연동 해제"""
        self.account_links = [
            link for link in self.account_links
            if link.bj_account_id.value != bj_account_id.value or link.deleted_at is not None
        ]
        self.updated_at = datetime.now()
        
    def set_target(self, target_id: TargetId) -> None:
        """도메인 로직 - 목표 설정 (기존 활성 목표가 있다면 삭제 후 신규 등록)"""
        
        # 1. 이미 동일한 타겟이 활성화되어 있는지 확인
        if self._has_target(target_id):
            return  # 혹은 raise APIException

        # 2. 기존에 존재하던 모든 활성 목표를 Soft Delete 처리
        for target in self.targets:
            if target.deleted_at is None:
                target.mark_as_deleted()

        # 3. 새로운 목표 추가
        self.targets.append(UserTarget.create(self.user_account_id, target_id))
        self.updated_at = datetime.now()
    
    def update_profile_image(self, profile_image: str) -> None:
        self.profile_image = profile_image
    
    def remove_target(self, target_id: TargetId) -> None:
        """도메인 로직 - 목표 제거"""
        for target in self.targets:
            if target.target_id.value == target_id.value:
                target.mark_as_deleted()
        self.updated_at = datetime.now()
    
    def _is_already_linked(self, bj_account_id: BaekjoonAccountId) -> bool:
        return any(
            link.bj_account_id.value == bj_account_id.value and link.deleted_at is None
            for link in self.account_links
        )
    
    def _has_target(self, target_id: TargetId) -> bool:
        return any(
            t.target_id.value == target_id.value and t.deleted_at is None
            for t in self.targets
        )