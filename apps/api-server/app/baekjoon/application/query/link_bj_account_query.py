from pydantic import BaseModel, Field


class LinkBaekjoonAccountResultQuery(BaseModel):
    """
    백준 계정 연동 결과 (Baekjoon → User)
    """

    bj_account_id: str = Field(..., description="백준 계정 ID (닉네임)")
    is_new_account: bool = Field(..., description="새로 생성된 계정 여부")