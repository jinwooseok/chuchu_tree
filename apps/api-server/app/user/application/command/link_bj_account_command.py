from pydantic import BaseModel, Field


class LinkBjAccountCommand(BaseModel):
    """
    백준 계정 연동 명령
    """

    user_account_id: int = Field(..., description="유저 계정 ID")
    bj_account_id: str = Field(..., description="백준 계정 ID")
    problem_count: int = Field(0, description="백준 계정의 문제 풀이 수")