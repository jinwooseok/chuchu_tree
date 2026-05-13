from dataclasses import dataclass


@dataclass
class TagCustomCommand:
    user_account_id: int
    tag_code: str
    tag_ban_yn: bool | None