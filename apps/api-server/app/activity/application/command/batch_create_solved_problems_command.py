from datetime import date
from pydantic import BaseModel, Field


class BatchCreateSolvedProblemsCommand(BaseModel):
    """여러 날짜의 문제를 한번에 추가하는 명령"""
    user_account_id: int = Field(..., description="유저 계정 ID")
    records: list[tuple[date, list[int]]] = Field(..., description="[(날짜, [문제ID들]), ...] 형태의 레코드 목록")
