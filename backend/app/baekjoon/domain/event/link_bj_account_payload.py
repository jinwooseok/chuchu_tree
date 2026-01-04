from pydantic import BaseModel, Field


class LinkBjAccountPayload(BaseModel):
    """
    백준 계정 연동 명령
    """

    user_account_id: int = Field(..., description="유저 계정 ID")
    bj_account_id: str = Field(..., description="백준 계정 ID")