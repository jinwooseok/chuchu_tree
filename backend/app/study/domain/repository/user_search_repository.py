from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class UserSearchResult:
    user_account_id: int
    bj_account_id: str
    user_code: str


class UserSearchRepository(ABC):
    @abstractmethod
    async def search_by_keyword(self, keyword: str, limit: int = 5) -> list[UserSearchResult]:
        ...

    @abstractmethod
    async def find_by_user_account_id(self, user_account_id: int) -> UserSearchResult | None:
        ...

    @abstractmethod
    async def find_by_user_account_ids(self, ids: list[int]) -> list[UserSearchResult]:
        ...
