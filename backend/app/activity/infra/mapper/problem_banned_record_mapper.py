"""ProblemBannedRecord Mapper"""
from app.activity.domain.entity.problem_banned_record import ProblemBannedRecord
from app.activity.infra.model.problem_banned_record import ProblemBannedRecordModel
from app.common.domain.vo.identifiers import ProblemId, UserAccountId
from datetime import datetime


class ProblemBannedRecordMapper:
    """ProblemBannedRecord Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: ProblemBannedRecordModel) -> ProblemBannedRecord:
        """Model -> Entity"""
        return ProblemBannedRecord(
            problem_banned_record_id=model.problem_banned_record_id,
            problem_id=ProblemId(model.problem_id),
            user_account_id=UserAccountId(model.user_account_id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )

    @staticmethod
    def to_model(entity: ProblemBannedRecord) -> ProblemBannedRecordModel:
        """Entity -> Model"""
        return ProblemBannedRecordModel(
            problem_banned_record_id=entity.problem_banned_record_id,
            problem_id=entity.problem_id.value,
            user_account_id=entity.user_account_id.value,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at,
        )
