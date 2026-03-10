from pydantic import BaseModel


class BjAccountSyncedPayload(BaseModel):
    user_account_id: int
    bj_account_id: str
    added_problem_ids: list[int]
    prev_tier_id: int | None
    new_tier_id: int | None
    log_type: str
    date: str
