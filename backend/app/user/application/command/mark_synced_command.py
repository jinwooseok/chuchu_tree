from pydantic import BaseModel, Field


class MarkSyncedCommand(BaseModel):
    """배치 동기화 완료 커맨드"""
    user_account_id: int = Field(..., description="유저 계정 ID")
