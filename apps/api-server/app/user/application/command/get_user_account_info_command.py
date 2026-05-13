from pydantic import BaseModel, Field


class GetUserAccountInfoCommand(BaseModel):
    """유저 계정 정보 조회 명령"""
    user_account_id: int = Field(..., description="유저 계정 ID")
