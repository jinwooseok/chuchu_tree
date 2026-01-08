from dataclasses import dataclass, field
from datetime import date, datetime

from app.activity.domain.entity.problem_banned_record import ProblemBannedRecord
from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.tag_customization import TagCustomization
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId, UserActivityId
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.common.domain.enums import ExcludedReason

@dataclass
class UserActivity:
    """Aggregate Root - 사용자 활동"""
    user_activity_id: UserActivityId|None
    user_account_id: UserAccountId
    will_solve_problems: list[WillSolveProblem] = field(default_factory=list)
    banned_problems: list[ProblemBannedRecord] = field(default_factory=list)
    solved_problems: list[ProblemRecord] = field(default_factory=list)
    tag_customizations: list[TagCustomization] = field(default_factory=list)
    
    @staticmethod
    def create(user_account_id: 'UserAccountId') -> 'UserActivity':
        """팩토리 메서드"""
        return UserActivity(
            user_activity_id=None,
            user_account_id=user_account_id,
            will_solve_problems=[],
            banned_problems=[],
            solved_problems=[],
            tag_customizations=[]
        )
    
    def mark_problem_to_solve(self, problem_id: ProblemId) -> None:
        """도메인 로직 - 풀 문제로 마킹"""
        if self._is_problem_banned(problem_id):
            raise APIException(ErrorCode.INVALID_INPUT_VALUE, message="Banned problem cannot be marked.")
        
        if self._is_already_marked(problem_id):
            # Or restore if it was deleted
            for problem in self.will_solve_problems:
                if problem.problem_id.value == problem_id.value:
                    problem.restore()
                    return
        
        self.will_solve_problems.append(
            WillSolveProblem.create(self.user_account_id, problem_id, date.today())
        )
    
    def unmark_problem(self, problem_id: 'ProblemId') -> None:
        """도메인 로직 - 문제 마킹 해제 (논리적 삭제)"""
        for problem in self.will_solve_problems:
            if problem.problem_id.value == problem_id.value and problem.deleted_at is None:
                problem.delete()
                break
    
    def ban_problem(self, problem_id: 'ProblemId') -> None:
        """도메인 로직 - 문제 제외"""
        if self._is_problem_banned(problem_id):
            return
        
        self.banned_problems.append(
            ProblemBannedRecord.create(problem_id, self.user_account_id)
        )
        self._remove_from_will_solve(problem_id)
    
    def record_problem_solved(self, problem_id: 'ProblemId') -> None:
        """도메인 로직 - 문제 해결 기록"""
        if self._is_already_solved(problem_id):
            return
        
        self.solved_problems.append(
            ProblemRecord.create(self.user_account_id, problem_id, date.today())
        )
        self._remove_from_will_solve(problem_id)
    
    def customize_tag(
        self,
        tag_id: TagId,
        exclude: bool,
        reason: ExcludedReason|None = None
    ) -> None:
        """도메인 로직 - 태그 커스터마이징 (Update or Create)"""
        
        existing_customization: TagCustomization | None = None
        for tc in self.tag_customizations:
            if tc.tag_id.value == tag_id.value and tc.deleted_at is None:
                existing_customization = tc
                break
        
        if existing_customization:
            existing_customization.excluded = exclude
            existing_customization.reason = reason
            existing_customization.updated_at = datetime.now()
        else:
            new_customization = TagCustomization.create(
                user_account_id=self.user_account_id,
                tag_id=tag_id,
                excluded=exclude,
                reason=reason
            )
            self.tag_customizations.append(new_customization)
            
    def remove_tag_customization(self, tag_id: TagId) -> None:
        """도메인 로직 - 태그 커스터마이징 제거 (논리적 삭제)"""
        
        existing_customization: TagCustomization | None = None
        for tc in self.tag_customizations:
            if tc.tag_id.value == tag_id.value and tc.deleted_at is None:
                existing_customization = tc
                break
        
        if existing_customization:
            existing_customization.deleted_at = datetime.now()
            existing_customization.updated_at = datetime.now()
    
    def get_excluded_tag_ids(self) -> list['TagId']:
        """제외된 태그 ID 목록 조회"""
        return [
            tc.tag_id for tc in self.tag_customizations
            if tc.excluded and tc.deleted_at is None
        ]
    
    def _is_problem_banned(self, problem_id: 'ProblemId') -> bool:
        return any(
            banned.problem_id.value == problem_id.value and banned.deleted_at is None
            for banned in self.banned_problems
        )
    
    def _is_already_marked(self, problem_id: 'ProblemId') -> bool:
        return any(
            problem.problem_id.value == problem_id.value and problem.deleted_at is None
            for problem in self.will_solve_problems
        )
    
    def _is_already_solved(self, problem_id: 'ProblemId') -> bool:
        return any(
            problem.problem_id.value == problem_id.value and problem.deleted_at is None
            for problem in self.solved_problems
        )
    
    def _remove_from_will_solve(self, problem_id: 'ProblemId') -> None:
        for problem in self.will_solve_problems:
            if problem.problem_id.value == problem_id.value:
                problem.delete()
                break