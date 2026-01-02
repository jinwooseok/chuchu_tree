from pydantic import BaseModel, Field


class LinkBaekjoonAccountRequest(BaseModel):
    """백준 계정 연동 요청"""
    bj_account: str = Field(..., alias="bjAccount", description="백준 계정 ID")

    class Config:
        populate_by_name = True
