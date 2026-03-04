from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from app.study.application.query.user_search_query import UserSearchItemQuery


class UserSearchItemResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    user_account_id: int
    bj_account_id: str
    user_code: str

    @classmethod
    def from_query(cls, q: UserSearchItemQuery) -> "UserSearchItemResponse":
        return cls(
            user_account_id=q.user_account_id,
            bj_account_id=q.bj_account_id,
            user_code=q.user_code,
        )


class UserSearchResponse(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

    users: list[UserSearchItemResponse]

    @classmethod
    def from_query(cls, queries: list[UserSearchItemQuery]) -> "UserSearchResponse":
        return cls(users=[UserSearchItemResponse.from_query(q) for q in queries])
