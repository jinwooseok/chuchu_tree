from dataclasses import dataclass


@dataclass
class UserSearchItemQuery:
    user_account_id: int
    bj_account_id: str
    user_code: str
