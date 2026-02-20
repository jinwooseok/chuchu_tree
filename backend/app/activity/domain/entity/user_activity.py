from dataclasses import dataclass, field
from datetime import date, datetime

from app.activity.domain.entity.problem_date_record import RecordType
from app.activity.domain.entity.tag_customization import TagCustomization
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.common.domain.vo.collections import ProblemIdSet, TagIdSet
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId, UserActivityId
from app.common.domain.enums import ExcludedReason
from app.core.error_codes import ErrorCode
from app.core.exception import APIException


@dataclass
class UserActivity:
    """Aggregate Root - 사용자 활동"""
    user_activity_id: UserActivityId | None
    user_account_id: UserAccountId
    problem_statuses: list[UserProblemStatus] = field(default_factory=list)
    tag_customizations: list[TagCustomization] = field(default_factory=list)

    @staticmethod
    def create(user_account_id: 'UserAccountId') -> 'UserActivity':
        """팩토리 메서드"""
        return UserActivity(
            user_activity_id=None,
            user_account_id=user_account_id,
            problem_statuses=[],
            tag_customizations=[]
        )

    # ===== 조회 편의 프로퍼티 =====

    @property
    def will_solve_problems(self) -> list[UserProblemStatus]:
        """활성 WILL_SOLVE 문제 목록"""
        return [
            s for s in self.problem_statuses
            if not s.banned_yn and not s.solved_yn and s._has_active_record(RecordType.WILL_SOLVE)
        ]

    @property
    def banned_problems(self) -> list[UserProblemStatus]:
        """활성 차단 문제 목록"""
        return [
            s for s in self.problem_statuses
            if s.banned_yn and s.deleted_at is None
        ]

    @property
    def solved_problems(self) -> list[UserProblemStatus]:
        """활성 해결된 문제 목록"""
        return [
            s for s in self.problem_statuses
            if s.solved_yn and not s.banned_yn and s.deleted_at is None
        ]

    # ===== 도메인 로직 =====

    def mark_problem_to_solve(self, problem_id: ProblemId) -> None:
        """풀 문제로 마킹"""
        if self._is_problem_banned(problem_id):
            raise APIException(ErrorCode.INVALID_INPUT_VALUE, message="Banned problem cannot be marked.")

        existing = self._find_status(problem_id)
        if existing:
            existing.restore()
            return

        self.problem_statuses.append(
            UserProblemStatus.create_will_solve(self.user_account_id, problem_id, date.today())
        )

    def unmark_problem(self, problem_id: 'ProblemId') -> None:
        """문제 마킹 해제 (논리적 삭제)"""
        existing = self._find_status(problem_id)
        if existing:
            for dr in existing.date_records:
                if dr.deleted_at is None and dr.record_type == RecordType.WILL_SOLVE:
                    dr.delete()

    def ban_problem(self, problem_id: 'ProblemId') -> None:
        """문제 차단"""
        if self._is_problem_banned(problem_id):
            return

        self.problem_statuses.append(
            UserProblemStatus.create_banned(self.user_account_id, problem_id)
        )

    def remove_ban_problem(self, problem_id: ProblemId) -> None:
        """문제 차단 해제 (논리적 삭제)"""
        for status in self.problem_statuses:
            if status.problem_id.value == problem_id.value and status.banned_yn and status.deleted_at is None:
                now = datetime.now()
                status.deleted_at = now
                status.updated_at = now
                break

    def record_problem_solved(self, problem_id: 'ProblemId') -> None:
        """문제 해결 기록"""
        if self._is_already_solved(problem_id):
            return

        self.problem_statuses.append(
            UserProblemStatus.create_solved(self.user_account_id, problem_id, date.today())
        )
        self._remove_from_will_solve(problem_id)

    def customize_tag(
        self,
        tag_id: TagId,
        exclude: bool,
        reason: ExcludedReason | None = None
    ) -> None:
        """태그 커스터마이징 (Update or Create)"""
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
        """태그 커스터마이징 제거 (논리적 삭제)"""
        for tc in self.tag_customizations:
            if tc.tag_id.value == tag_id.value and tc.deleted_at is None:
                tc.deleted_at = datetime.now()
                tc.updated_at = datetime.now()
                break

    def get_excluded_tag_ids(self) -> list['TagId']:
        """제외된 태그 ID 목록 조회"""
        return [
            tc.tag_id for tc in self.tag_customizations
            if tc.excluded and tc.deleted_at is None
        ]

    # ===== ID 집합 프로퍼티 =====

    @property
    def solved_problem_ids(self) -> ProblemIdSet:
        ids = {s.problem_id for s in self.solved_problems}
        return ProblemIdSet.from_ids(ids)

    @property
    def banned_problem_ids(self) -> ProblemIdSet:
        ids = {s.problem_id for s in self.banned_problems}
        return ProblemIdSet.from_ids(ids)

    @property
    def excluded_tag_ids(self) -> TagIdSet:
        ids = {tc.tag_id for tc in self.tag_customizations
               if tc.excluded and tc.deleted_at is None}
        return TagIdSet.from_ids(ids)

    @property
    def will_solve_problem_ids(self) -> ProblemIdSet:
        ids = {s.problem_id for s in self.will_solve_problems}
        return ProblemIdSet.from_ids(ids)

    # ===== 내부 헬퍼 =====

    def _find_status(self, problem_id: 'ProblemId') -> UserProblemStatus | None:
        for s in self.problem_statuses:
            if s.problem_id.value == problem_id.value:
                return s
        return None

    def _is_problem_banned(self, problem_id: 'ProblemId') -> bool:
        return any(
            s.problem_id.value == problem_id.value and s.banned_yn and s.deleted_at is None
            for s in self.problem_statuses
        )

    def _is_already_marked(self, problem_id: 'ProblemId') -> bool:
        return any(
            s.problem_id.value == problem_id.value and s._has_active_record(RecordType.WILL_SOLVE)
            for s in self.problem_statuses
        )

    def _is_already_solved(self, problem_id: 'ProblemId') -> bool:
        return any(
            s.problem_id.value == problem_id.value and s.solved_yn and s.deleted_at is None
            for s in self.problem_statuses
        )

    def _remove_from_will_solve(self, problem_id: 'ProblemId') -> None:
        existing = self._find_status(problem_id)
        if existing:
            for dr in existing.date_records:
                if dr.deleted_at is None and dr.record_type == RecordType.WILL_SOLVE:
                    dr.delete()
