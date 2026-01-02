from pydantic import BaseModel, Field
from typing import List


class TierStat(BaseModel):
    """티어 통계"""
    tier_id: int = Field(..., alias="tierId")
    tier_name: str = Field(..., alias="tierName")
    longest_streak: int = Field(..., alias="longestStreak")
    rating: int
    class_level: int = Field(..., alias="class")
    tier_start_date: str = Field(..., alias="tierStartDate")

    class Config:
        populate_by_name = True


class StreakItem(BaseModel):
    """스트릭 항목"""
    problem_history_id: int = Field(..., alias="problemHistoryId")
    solved_count: int = Field(..., alias="solvedCount")
    solved_date: str = Field(..., alias="solvedDate")

    class Config:
        populate_by_name = True


class UserAccountInfo(BaseModel):
    """유저 계정 정보"""
    user_account_id: int = Field(..., alias="userAccountId")
    profile_image_url: str | None = Field(None, alias="profileImageUrl")
    registered_at: str = Field(..., alias="registeredAt")

    class Config:
        populate_by_name = True


class BaekjoonAccountInfo(BaseModel):
    """백준 계정 정보"""
    bj_account_id: int = Field(..., alias="bjAccountId")
    stat: TierStat
    streaks: List[StreakItem]
    registered_at: str = Field(..., alias="registeredAt")

    class Config:
        populate_by_name = True


class BaekjoonMeResponse(BaseModel):
    """유저 기본정보 조회 응답"""
    user_account: UserAccountInfo = Field(..., alias="userAccount")
    bj_account: BaekjoonAccountInfo = Field(..., alias="bjAccount")
    linked_at: str = Field(..., alias="linkedAt")

    class Config:
        populate_by_name = True


class StreakResponse(BaseModel):
    """스트릭 조회 응답"""
    streaks: List[StreakItem]

    class Config:
        populate_by_name = True


class TagTarget(BaseModel):
    """태그 목표"""
    target_id: int = Field(..., alias="targetId")
    target_code: str = Field(..., alias="targetCode")
    target_display_name: str = Field(..., alias="targetDisplayName")

    class Config:
        populate_by_name = True


class TagAlias(BaseModel):
    """태그 별칭"""
    alias: str

    class Config:
        populate_by_name = True


class TagInfo(BaseModel):
    """태그 정보"""
    tag_id: int = Field(..., alias="tagId")
    tag_code: str = Field(..., alias="tagCode")
    tag_display_name: str = Field(..., alias="tagDisplayName")
    tag_target: List[TagTarget] | None = Field(None, alias="tagTarget")
    tag_aliases: List[TagAlias] = Field(default_factory=list, alias="tagAliases")

    class Config:
        populate_by_name = True


class ProblemInfo(BaseModel):
    """문제 정보"""
    problem_id: int = Field(..., alias="problemId")
    problem_title: str = Field(..., alias="problemTitle")
    problem_tier_level: int = Field(..., alias="problemTierLevel")
    problem_tier_name: str = Field(..., alias="problemTierName")
    problem_class_level: int = Field(..., alias="problemClassLevel")
    tags: List[TagInfo]

    class Config:
        populate_by_name = True


class SolvedProblemInfo(ProblemInfo):
    """풀은 문제 정보"""
    real_solved_yn: bool = Field(..., alias="realSolvedYn")

    class Config:
        populate_by_name = True


class MonthlyProblemData(BaseModel):
    """월간 문제 데이터"""
    date: str
    solved_problem_count: int = Field(..., alias="solvedProblemCount")
    will_solve_problem_count: int = Field(..., alias="willSolveProblemCount")
    solved_problems: List[SolvedProblemInfo] = Field(..., alias="solvedProblems")
    will_solve_problem: List[ProblemInfo] = Field(..., alias="willSolveProblem")

    class Config:
        populate_by_name = True


class MonthlyProblemsResponse(BaseModel):
    """월간 문제 상세 정보 조회 응답"""
    total_problem_count: int = Field(..., alias="totalProblemCount")
    monthly_data: List[MonthlyProblemData] = Field(..., alias="monthlyData")

    class Config:
        populate_by_name = True


class BaekjoonAccountItem(BaseModel):
    """백준 계정 항목 (Admin)"""
    bj_account_id: int = Field(..., alias="bjAccountId")
    stat: TierStat
    registered_at: str = Field(..., alias="registeredAt")

    class Config:
        populate_by_name = True


class AdminBaekjoonAccountsResponse(BaseModel):
    """관리자 백준 계정 목록 응답"""
    bj_accounts: List[BaekjoonAccountItem] = Field(..., alias="bjAccounts")

    class Config:
        populate_by_name = True
