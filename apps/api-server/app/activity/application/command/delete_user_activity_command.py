"""Activity 모듈 삭제 Command 객체"""

from pydantic import BaseModel, Field


class DeleteUserActivityCommand(BaseModel):
    """
    사용자 활동 데이터 삭제 명령
    """

    user_account_id: int = Field(..., description="삭제할 사용자 계정 ID")
