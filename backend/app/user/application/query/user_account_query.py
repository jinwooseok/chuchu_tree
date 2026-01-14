"""User 모듈 Query 객체"""

from pydantic import BaseModel, Field


class CreateUserAccountQuery(BaseModel):
    """
    사용자 계정 쿼리 결과

    User 모듈이 반환하는 결과 객체입니다.
    이 객체는 wrapper에 의해 dict로 변환된 후, 호출자가 원하는 타입으로 재조립됩니다.
    """

    user_account_id: int = Field(..., description="사용자 계정 ID")
    new_user_yn: bool = Field(..., description="신규 생성 여부")
