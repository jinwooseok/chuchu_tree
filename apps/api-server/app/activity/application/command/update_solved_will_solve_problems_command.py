from datetime import date
from pydantic import BaseModel, Field


class UpdateSolvedAndWillSolveProblemsCommand(BaseModel):
    user_account_id: int = Field(..., description="유저 계정 ID")
    solved_date: date = Field(..., description="날짜 (YYYY-MM-DD)")
    solved_problem_ids: list[int] = Field(..., description="풀었던 문제 ID 목록")
    will_solve_problem_ids: list[int] = Field(..., description="풀 예정 문제 ID 목록")
