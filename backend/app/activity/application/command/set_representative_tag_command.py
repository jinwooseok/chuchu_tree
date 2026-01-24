"""대표 태그 설정 Command 객체"""

from pydantic import BaseModel, Field


class SetProblemRepresentativeTagCommand(BaseModel):
    """
    문제 대표 태그 설정 명령 (통합)
    solved_problem과 will_solve_problem 모두 자동 감지하여 설정
    """

    user_account_id: int = Field(..., description="사용자 계정 ID")
    problem_id: int = Field(..., description="문제 ID")
    representative_tag_code: str | None = Field(None, description="대표 태그 코드 (None이면 대표 태그 해제)")
