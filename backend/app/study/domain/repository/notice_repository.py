from abc import ABC, abstractmethod

from app.common.domain.vo.identifiers import NoticeId, UserAccountId
from app.study.domain.entity.notice import Notice


class NoticeRepository(ABC):
    @abstractmethod
    async def insert(self, notice: Notice) -> Notice:
        ...

    @abstractmethod
    async def find_by_id(self, notice_id: int) -> Notice | None:
        ...

    @abstractmethod
    async def insert_many(self, notices: list[Notice]) -> list[Notice]:
        ...

    @abstractmethod
    async def find_by_recipient(self, user_account_id: UserAccountId, limit: int = 50) -> list[Notice]:
        ...

    @abstractmethod
    async def find_unread_count_by_recipient(self, user_account_id: UserAccountId) -> int:
        ...

    @abstractmethod
    async def update(self, notice: Notice) -> Notice:
        ...

    @abstractmethod
    async def mark_all_read_by_recipient(self, user_account_id: UserAccountId) -> None:
        ...
