from pydantic import BaseModel, Field


class GetUnrecordedProblemsCommand(BaseModel):
    """백준 내 정보 조회 명령"""
    user_account_id: int = Field(..., description="유저 계정 ID")
