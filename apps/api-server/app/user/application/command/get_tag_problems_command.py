"""태그 별 푼 문제 조회 Command"""

from dataclasses import dataclass


@dataclass
class GetTagProblemsCommand:
    """태그 별 푼 문제 조회 커맨드"""
    user_account_id: int
    tag_code: str
