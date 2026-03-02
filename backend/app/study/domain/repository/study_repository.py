from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.common.domain.vo.identifiers import StudyId, UserAccountId
from app.study.domain.entity.study import Study


@dataclass(frozen=True)
class StudySearchResult:
    study_id: int
    study_name: str
    owner_bj_account_id: str
    owner_user_code: str
    member_count: int


class StudyRepository(ABC):
    @abstractmethod
    async def insert(self, study: Study) -> Study:
        ...

    @abstractmethod
    async def find_by_id(self, study_id: StudyId) -> Study | None:
        ...

    @abstractmethod
    async def find_by_name(self, name: str) -> Study | None:
        ...

    @abstractmethod
    async def search(self, keyword: str, limit: int = 5) -> list[StudySearchResult]:
        ...

    @abstractmethod
    async def find_by_member_user_account_id(self, user_account_id: UserAccountId) -> list[Study]:
        ...

    @abstractmethod
    async def update(self, study: Study) -> Study:
        ...

    @abstractmethod
    async def soft_delete(self, study: Study) -> None:
        ...

    @abstractmethod
    async def is_name_taken(self, name: str) -> bool:
        ...
