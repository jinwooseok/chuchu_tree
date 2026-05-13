from pydantic import BaseModel


class CreateNoticeCommand(BaseModel):
    recipient_user_account_id: int
    category: str
    category_detail: str
    content: dict


class HandleBjSyncedCommand(BaseModel):
    user_account_id: int
    bj_account_id: str
    added_problem_ids: list[int]
    prev_tier_id: int | None
    new_tier_id: int | None
    log_type: str
    date: str


class HandleBatchProblemsUpdatedCommand(BaseModel):
    user_account_id: int
    problem_ids: list[int]
    date: str
