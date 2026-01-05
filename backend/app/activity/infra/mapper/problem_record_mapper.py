"""ProblemRecord Mapper"""
from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.infra.model.problem_record import ProblemRecordModel
from app.common.domain.vo.identifiers import ProblemId, UserAccountId


class ProblemRecordMapper:
    """ProblemRecord Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: ProblemRecordModel) -> ProblemRecord:
        """Model -> Entity"""
        return ProblemRecord(
            problem_record_id=model.problem_record_id,
            user_account_id=UserAccountId(model.user_account_id),
            problem_id=ProblemId(model.problem_id),
            marked_date=model.marked_date,
            solved=model.solved_yn,
            memo_title=model.memo_title,
            content=model.content,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: ProblemRecord) -> ProblemRecordModel:
        """Entity -> Model"""
        return ProblemRecordModel(
            problem_record_id=entity.problem_record_id,
            user_account_id=entity.user_account_id.value,
            problem_id=entity.problem_id.value,
            marked_date=entity.marked_date,
            solved_yn=entity.solved,
            memo_title=entity.memo_title,
            content=entity.content,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
