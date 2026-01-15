from dataclasses import dataclass


@dataclass
class BanProblemCommand:
    user_account_id: int
    problem_id: int
    problem_ban_yn: bool | None