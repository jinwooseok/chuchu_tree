from dataclasses import dataclass
from datetime import datetime

from app.common.domain.vo.identifiers import ProblemId


@dataclass
class ProblemUpdateHistory:
    """Entity - 문제 변경 히스토리"""
    problem_update_history_id: int|None
    problem_id: ProblemId
    update_log: dict[str, any]  # JSON
    created_at: datetime
    
    @staticmethod
    def create(
        problem_id: ProblemId,
        field: str,
        old_value: any,
        new_value: any
    ) -> 'ProblemUpdateHistory':
        return ProblemUpdateHistory(
            problem_update_history_id=None,
            problem_id=problem_id,
            update_log={
                "field": field,
                "old_value": old_value,
                "new_value": new_value,
                "changed_at": datetime.now().isoformat()
            },
            created_at=datetime.now()
        )