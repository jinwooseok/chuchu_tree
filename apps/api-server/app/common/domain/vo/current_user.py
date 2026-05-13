from dataclasses import dataclass

@dataclass(frozen=True)
class CurrentUser:
    user_account_id: int