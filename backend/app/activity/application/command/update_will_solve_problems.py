from datetime import date
from pydantic import BaseModel, Field


class UpdateWillSolveProblemCommand(BaseModel):
    user_account_id: int = Field(..., description="유저 계정 ID")
    solved_date: date = Field(..., description="날짜 (YYYY-MM-DD)")
    problem_ids: list[int] = Field(..., alias="problemId", description="문제 ID 목록")
    
        