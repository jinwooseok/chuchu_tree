"""WillSolveProblem Mapper"""
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.infra.model.will_solve_problem import WillSolveProblemModel
from app.common.domain.vo.identifiers import ProblemId, UserAccountId


class WillSolveProblemMapper:
    """WillSolveProblem Entity <-> Model 변환"""

    @staticmethod
    def to_entity(model: WillSolveProblemModel) -> WillSolveProblem:
        """Model -> Entity"""
        return WillSolveProblem(
            will_solve_problem_id=model.will_solve_problem_id,
            user_account_id=UserAccountId(model.user_account_id),
            problem_id=ProblemId(model.problem_id),
            solved=model.solved,
            marked_date=model.marked_date,
            order=model.order,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at
        )

    @staticmethod
    def to_model(entity: WillSolveProblem) -> WillSolveProblemModel:
        """Entity -> Model"""
        return WillSolveProblemModel(
            will_solve_problem_id=entity.will_solve_problem_id,
            user_account_id=entity.user_account_id.value,
            problem_id=entity.problem_id.value,
            solved=entity.solved,
            marked_date=entity.marked_date,
            order=entity.order,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
            deleted_at=entity.deleted_at
        )
