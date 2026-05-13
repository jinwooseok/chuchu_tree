from datetime import datetime
from pydantic import BaseModel, Field
from typing import List


class ProfileImageResponse(BaseModel):
    """프로필 사진 설정 응답"""
    profile_image_url: str = Field(..., alias="profileImageUrl")

    class Config:
        populate_by_name = True


class UserAccountItem(BaseModel):
    """유저 계정 항목"""
    user_account_id: int = Field(..., alias="userAccountId")
    linked_bj_account_id: int | None = Field(None, alias="linkedBjAccountId")
    profile_image_url: str | None = Field(None, alias="profileImageUrl")
    provider: str = Field(..., description="KAKAO, GOOGLE, NAVER, GITHUB")
    registered_at: str = Field(..., alias="registeredAt")

    class Config:
        populate_by_name = True


class AdminUserAccountsResponse(BaseModel):
    """관리자 유저 계정 목록 응답"""
    current_page: int = Field(..., alias="currentPage")
    size: int
    total_page: int = Field(..., alias="totalPage")
    total_count: int = Field(..., alias="totalCount")
    user_accounts: List[UserAccountItem] = Field(..., alias="userAccounts")

    class Config:
        populate_by_name = True
