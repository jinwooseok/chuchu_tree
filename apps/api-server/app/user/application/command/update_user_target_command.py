"""유저 태그 목록 조회 Command"""

from dataclasses import dataclass


@dataclass
class UpdateUserTargetCommand:
    """유저 태그 목록 조회 커맨드"""
    user_account_id: int
    target_code: str
