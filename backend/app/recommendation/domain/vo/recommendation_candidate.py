"""추천 후보 Value Object"""

from dataclasses import dataclass

from app.problem.domain.entity.problem import Problem


@dataclass(frozen=True)
class RecommendationCandidate:
    """추천 문제 후보 VO"""
    problem: Problem
    reason: str
    tag_name: str

    @staticmethod
    def create(problem: Problem, reason: str, tag_name: str) -> 'RecommendationCandidate':
        """팩토리 메서드"""
        return RecommendationCandidate(
            problem=problem,
            reason=reason,
            tag_name=tag_name
        )
