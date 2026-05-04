"""UserProblemStatus Mapper - 정규화된 테이블과 도메인 엔티티 간 1:1 변환"""
from datetime import datetime
from sqlalchemy import inspect
from app.activity.domain.entity.problem_date_record import ProblemDateRecord, RecordType
from app.activity.domain.entity.user_problem_status import UserProblemStatus
from app.activity.infra.model.problem_date_record import ProblemDateRecordModel
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.common.domain.vo.identifiers import ProblemId, TagId, UserAccountId


class UserProblemStatusMapper:
    """UserProblemStatus 도메인 엔티티 <-> DB 모델 변환

    DB 구조:
    - UserProblemStatusModel: 마스터 (1)
    - ProblemDateRecordModel: 날짜 디테일 (N)

    도메인 엔티티:
    - UserProblemStatus: 마스터 + date_records 포함
    - ProblemDateRecord: 날짜 레코드
    """

    @staticmethod
    def date_record_to_entity(model: ProblemDateRecordModel) -> ProblemDateRecord:
        """ProblemDateRecordModel -> ProblemDateRecord"""
        return ProblemDateRecord(
            problem_date_record_id=model.problem_date_record_id,
            user_problem_status_id=model.user_problem_status_id,
            marked_date=model.marked_date,
            record_type=RecordType(model.record_type.value),
            display_order=model.display_order,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def status_to_entity(
        status_model: UserProblemStatusModel,
        date_record_models: list[ProblemDateRecordModel] | None = None
    ) -> UserProblemStatus:
        """UserProblemStatusModel (+ optional date_records) -> UserProblemStatus"""
        date_records = []
        ins = inspect(status_model)
        if "date_records" not in ins.unloaded:
            date_records = [
                UserProblemStatusMapper.date_record_to_entity(dr)
                for dr in (date_record_models or status_model.date_records or [])
            ]
        return UserProblemStatus(
            user_problem_status_id=status_model.user_problem_status_id,
            user_account_id=UserAccountId(status_model.user_account_id),
            problem_id=ProblemId(status_model.problem_id),
            banned_yn=status_model.banned_yn,
            solved_yn=status_model.solved_yn,
            representative_tag_id=TagId(status_model.representative_tag_id) if status_model.representative_tag_id else None,
            memo_title=status_model.memo_title,
            content=status_model.content,
            date_records=date_records,
            bj_account_id=status_model.bj_account_id,
            created_at=status_model.created_at,
            updated_at=status_model.updated_at,
            deleted_at=status_model.deleted_at
        )

    @staticmethod
    def entity_to_status_model(
        entity: UserProblemStatus,
        existing: UserProblemStatusModel | None = None
    ) -> UserProblemStatusModel:
        """UserProblemStatus -> UserProblemStatusModel (create or update)"""
        if existing:
            existing.banned_yn = entity.banned_yn
            existing.solved_yn = entity.solved_yn
            existing.representative_tag_id = (
                entity.representative_tag_id.value if entity.representative_tag_id else None
            )
            existing.memo_title = entity.memo_title
            existing.content = entity.content
            existing.updated_at = entity.updated_at
            existing.deleted_at = entity.deleted_at
            return existing

        return UserProblemStatusModel(
            user_account_id=entity.user_account_id.value,
            bj_account_id=entity.bj_account_id,
            problem_id=entity.problem_id.value,
            banned_yn=entity.banned_yn,
            solved_yn=entity.solved_yn,
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
    def entity_to_date_record_model(
        date_record: ProblemDateRecord,
        status_id: int,
        existing: ProblemDateRecordModel | None = None
    ) -> ProblemDateRecordModel:
        """ProblemDateRecord -> ProblemDateRecordModel (create or update)"""
        from app.activity.infra.model.problem_date_record import RecordType as ModelRecordType
        if existing:
            existing.marked_date = date_record.marked_date
            existing.display_order = date_record.display_order
            existing.updated_at = date_record.updated_at
            existing.deleted_at = date_record.deleted_at
            return existing

        return ProblemDateRecordModel(
            problem_date_record_id=date_record.problem_date_record_id,
            user_problem_status_id=status_id,
            marked_date=date_record.marked_date,
            record_type=ModelRecordType(date_record.record_type.value),
            display_order=date_record.display_order,
            created_at=date_record.created_at,
            updated_at=date_record.updated_at,
            deleted_at=date_record.deleted_at
        )
