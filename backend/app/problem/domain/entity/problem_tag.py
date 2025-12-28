from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import ProblemId, TagId


@dataclass
class ProblemTag:
    """Entity - 문제-태그 매핑"""
    problem_tag_id: int|None
    problem_id: ProblemId
    tag_id: TagId
    created_at: datetime
    
    @staticmethod
    def create(problem_id: ProblemId, tag_id: TagId) -> 'ProblemTag':
        return ProblemTag(
            problem_tag_id=None,
            problem_id=problem_id,
            tag_id=tag_id,
            created_at=datetime.now()
        )