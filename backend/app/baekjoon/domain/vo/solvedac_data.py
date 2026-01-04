"""solved.ac API 응답 데이터를 위한 Value Objects"""

from dataclasses import dataclass
from datetime import datetime, date


@dataclass(frozen=True)
class ProblemTagVO:
    """문제 태그 정보"""

    key: str
    boj_tag_id: int
    display_name_ko: str | None


@dataclass(frozen=True)
class SolvedProblemVO:
    """푼 문제 정보"""

    problem_id: int
    title_ko: str
    level: int
    tags: list[ProblemTagVO]

    @classmethod
    def from_api_response(cls, data: dict) -> "SolvedProblemVO":
        """solved.ac API 응답을 VO로 변환"""
        tags = []
        for tag_data in data.get("tags", []):
            display_names = tag_data.get("displayNames", [])
            ko_name = None
            for display in display_names:
                if display.get("language") == "ko":
                    ko_name = display.get("name")
                    break

            tags.append(ProblemTagVO(
                key=tag_data.get("key", ""),
                boj_tag_id=tag_data.get("bojTagId", 0),
                display_name_ko=ko_name
            ))

        return cls(
            problem_id=data.get("problemId", 0),
            title_ko=data.get("titleKo", ""),
            level=data.get("level", 0),
            tags=tags
        )


@dataclass(frozen=True)
class UserHistoryItemVO:
    """유저 히스토리 항목 (solved.ac API의 user/history 응답)"""

    timestamp: str
    solved_count: int

    @classmethod
    def from_api_response(cls, data: dict) -> "UserHistoryItemVO":
        """solved.ac API 응답을 VO로 변환"""
        return cls(
            timestamp=data.get("timestamp", ""),
            solved_count=data.get("value", 0)
        )


@dataclass(frozen=True)
class SolvedacUserInfoVO:
    """solved.ac 유저 정보 (user/show API 응답)"""

    handle: str
    tier: int
    rating: int
    class_level: int
    solved_count: int
    max_streak: int
    joined_at: str

    @classmethod
    def from_api_response(cls, data: dict) -> "SolvedacUserInfoVO":
        """solved.ac API 응답을 VO로 변환"""
        return cls(
            handle=data.get("handle", ""),
            tier=data.get("tier", 0),
            rating=data.get("rating", 0),
            class_level=data.get("class", 0),
            solved_count=data.get("solvedCount", 0),
            max_streak=data.get("maxStreak", 0),
            joined_at=data.get("joinedAt", "")
        )


@dataclass(frozen=True)
class SolvedacUserDataVO:
    """solved.ac에서 수집한 유저 전체 데이터"""

    user_id: str
    user_info: SolvedacUserInfoVO
    total_count: int
    problems: list[SolvedProblemVO]
    history: list[UserHistoryItemVO]
    collected_at: datetime

    @classmethod
    def from_collector_response(cls, data: dict) -> "SolvedacUserDataVO":
        """Collector 응답을 VO로 변환"""
        problems = [
            SolvedProblemVO.from_api_response(item)
            for item in data.get("items", [])
        ]

        history = [
            UserHistoryItemVO.from_api_response(item)
            for item in data.get("history", [])
        ]

        user_info = SolvedacUserInfoVO.from_api_response(data.get("user_info", {}))

        collected_at_str = data.get("collected_at")
        if isinstance(collected_at_str, str):
            collected_at = datetime.fromisoformat(collected_at_str)
        else:
            collected_at = datetime.now()

        return cls(
            user_id=data.get("user_id", ""),
            user_info=user_info,
            total_count=data.get("total_count", 0),
            problems=problems,
            history=history,
            collected_at=collected_at
        )
