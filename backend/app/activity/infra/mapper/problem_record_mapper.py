"""ProblemRecord Mapper - 정규화된 테이블 매핑

UserProblemStatus (마스터) + ProblemDateRecord (디테일) <-> Domain Entities
"""
from datetime import datetime

from app.activity.domain.entity.problem_banned_record import ProblemBannedRecord
from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.activity.infra.model.problem_date_record import ProblemDateRecordModel, RecordType
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId


class ProblemRecordMapper:
    """정규화된 테이블 구조와 도메인 엔티티 간 변환

    테이블 구조:
    - UserProblemStatusModel: 문제별 단일 레코드 (banned_yn, solved_yn, representative_tag_id 등)
    - ProblemDateRecordModel: 날짜별 1:N 레코드 (marked_date, record_type, display_order)

    도메인 엔티티:
    - ProblemRecord: solved_yn=true + record_type='SOLVED'
    - WillSolveProblem: solved_yn=false, banned_yn=false + record_type='WILL_SOLVE'
    - ProblemBannedRecord: banned_yn=true (날짜 레코드 없음)
    """

    # ========== ProblemRecord 변환 (solved_yn=true) ==========

    @staticmethod
    def to_entity(
        status: UserProblemStatusModel,
        date_record: ProblemDateRecordModel
    ) -> ProblemRecord:
        """Models -> ProblemRecord Entity"""
        return ProblemRecord(
            problem_record_id=date_record.problem_date_record_id,
            user_account_id=UserAccountId(status.user_account_id),
            problem_id=ProblemId(status.problem_id),
            marked_date=date_record.marked_date,
            solved=status.solved_yn,
            representative_tag_id=TagId(status.representative_tag_id) if status.representative_tag_id else None,
            memo_title=status.memo_title,
            order=date_record.display_order,
            content=status.content,
            created_at=date_record.created_at,
            updated_at=date_record.updated_at,
            deleted_at=date_record.deleted_at
        )

    @staticmethod
    def to_status_model(
        entity: ProblemRecord,
        existing_status: UserProblemStatusModel | None = None
    ) -> UserProblemStatusModel:
        """ProblemRecord Entity -> UserProblemStatusModel

        Args:
            entity: 도메인 엔티티
            existing_status: 기존 status 모델 (있으면 업데이트, 없으면 생성)
        """
        if existing_status:
            existing_status.solved_yn = True
            existing_status.representative_tag_id = (
                entity.representative_tag_id.value if entity.representative_tag_id else None
            )
            existing_status.memo_title = entity.memo_title
            existing_status.content = entity.content
            existing_status.updated_at = entity.updated_at
            existing_status.deleted_at = entity.deleted_at
            return existing_status

        return UserProblemStatusModel(
            user_account_id=entity.user_account_id.value,
            problem_id=entity.problem_id.value,
            banned_yn=False,
            solved_yn=entity.solved,
            representative_tag_id=(
                entity.representative_tag_id.value if entity.representative_tag_id else None
            ),
            memo_title=entity.memo_title,
            content=entity.content,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )

    @staticmethod
    def to_date_record_model(
        entity: ProblemRecord,
        status_id: int,
        existing_record: ProblemDateRecordModel | None = None
    ) -> ProblemDateRecordModel:
        """ProblemRecord Entity -> ProblemDateRecordModel"""
        if existing_record:
            existing_record.marked_date = entity.marked_date
            existing_record.display_order = entity.order
            existing_record.updated_at = entity.updated_at
            existing_record.deleted_at = entity.deleted_at
            return existing_record

        return ProblemDateRecordModel(
            problem_date_record_id=entity.problem_record_id,
            user_problem_status_id=status_id,
            marked_date=entity.marked_date,
            record_type=RecordType.SOLVED,
            display_order=entity.order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )

    # ========== WillSolveProblem 변환 (solved_yn=false, banned_yn=false) ==========

    @staticmethod
    def to_will_solve_entity(
        status: UserProblemStatusModel,
        date_record: ProblemDateRecordModel
    ) -> WillSolveProblem:
        """Models -> WillSolveProblem Entity"""
        return WillSolveProblem(
            will_solve_problem_id=date_record.problem_date_record_id,
            user_account_id=UserAccountId(status.user_account_id),
            problem_id=ProblemId(status.problem_id),
            solved=status.solved_yn,
            marked_date=date_record.marked_date,
            order=date_record.display_order,
            representative_tag_id=TagId(status.representative_tag_id) if status.representative_tag_id else None,
            created_at=date_record.created_at,
            updated_at=date_record.updated_at,
            deleted_at=date_record.deleted_at
        )

    @staticmethod
    def from_will_solve_to_status_model(
        entity: WillSolveProblem,
        existing_status: UserProblemStatusModel | None = None
    ) -> UserProblemStatusModel:
        """WillSolveProblem Entity -> UserProblemStatusModel"""
        if existing_status:
            existing_status.representative_tag_id = (
                entity.representative_tag_id.value if entity.representative_tag_id else None
            )
            existing_status.updated_at = entity.updated_at
            return existing_status

        return UserProblemStatusModel(
            user_account_id=entity.user_account_id.value,
            problem_id=entity.problem_id.value,
            banned_yn=False,
            solved_yn=entity.solved,
            representative_tag_id=(
                entity.representative_tag_id.value if entity.representative_tag_id else None
            ),
            memo_title=None,
            content=None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=None  # status는 deleted_at 별도 관리
        )

    @staticmethod
    def from_will_solve_to_date_record(
        entity: WillSolveProblem,
        status_id: int,
        existing_record: ProblemDateRecordModel | None = None
    ) -> ProblemDateRecordModel:
        """WillSolveProblem Entity -> ProblemDateRecordModel"""
        if existing_record:
            existing_record.marked_date = entity.marked_date
            existing_record.display_order = entity.order
            existing_record.updated_at = entity.updated_at
            existing_record.deleted_at = entity.deleted_at
            return existing_record

        return ProblemDateRecordModel(
            problem_date_record_id=entity.will_solve_problem_id,
            user_problem_status_id=status_id,
            marked_date=entity.marked_date,
            record_type=RecordType.WILL_SOLVE,
            display_order=entity.order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )

    # ========== ProblemBannedRecord 변환 (banned_yn=true) ==========

    @staticmethod
    def to_banned_entity(status: UserProblemStatusModel) -> ProblemBannedRecord:
        """UserProblemStatusModel -> ProblemBannedRecord Entity

        Note: banned 상태는 날짜 레코드가 없음 (status만 사용)
        """
        return ProblemBannedRecord(
            problem_banned_record_id=status.user_problem_status_id,
            problem_id=ProblemId(status.problem_id),
            user_account_id=UserAccountId(status.user_account_id),
            created_at=status.created_at,
            updated_at=status.updated_at,
            deleted_at=status.deleted_at
        )

    @staticmethod
    def from_banned_to_status_model(
        entity: ProblemBannedRecord,
        existing_status: UserProblemStatusModel | None = None
    ) -> UserProblemStatusModel:
        """ProblemBannedRecord Entity -> UserProblemStatusModel

        Note: banned 상태는 날짜 레코드 없이 status만 저장
        """
        if existing_status:
            existing_status.banned_yn = True
            existing_status.updated_at = entity.updated_at
            existing_status.deleted_at = entity.deleted_at
            return existing_status

        return UserProblemStatusModel(
            user_problem_status_id=entity.problem_banned_record_id,
            user_account_id=entity.user_account_id.value,
            problem_id=entity.problem_id.value,
            banned_yn=True,
            solved_yn=False,
            representative_tag_id=None,
            memo_title=None,
            content=None,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
