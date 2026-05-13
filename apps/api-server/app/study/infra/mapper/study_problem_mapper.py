from app.common.domain.vo.identifiers import (
    ProblemId,
    StudyId,
    StudyProblemId,
    StudyProblemMemberId,
    UserAccountId,
)
from app.study.domain.entity.study_problem import StudyProblem, StudyProblemMember
from app.study.infra.model.study_problem import StudyProblemModel
from app.study.infra.model.study_problem_member import StudyProblemMemberModel


class StudyProblemMapper:
    @staticmethod
    def to_model(entity: StudyProblem) -> StudyProblemModel:
        model = StudyProblemModel()
        if entity.study_problem_id is not None:
            model.study_problem_id = entity.study_problem_id.value
        model.study_id = entity.study_id.value
        model.problem_id = entity.problem_id.value
        model.assigned_by_user_account_id = entity.assigned_by_user_account_id.value
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model

    @staticmethod
    def to_entity(model: StudyProblemModel) -> StudyProblem:
        members = []
        if model.members:
            members = [StudyProblemMapper.member_to_entity(m) for m in model.members]
        return StudyProblem(
            study_problem_id=StudyProblemId(model.study_problem_id),
            study_id=StudyId(model.study_id),
            problem_id=ProblemId(model.problem_id),
            assigned_by_user_account_id=UserAccountId(model.assigned_by_user_account_id),
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
            members=members,
        )

    @staticmethod
    def member_to_model(entity: StudyProblemMember) -> StudyProblemMemberModel:
        model = StudyProblemMemberModel()
        if entity.study_problem_member_id is not None:
            model.study_problem_member_id = entity.study_problem_member_id.value
        if entity.study_problem_id is not None:
            model.study_problem_id = entity.study_problem_id.value
        model.user_account_id = entity.user_account_id.value
        model.target_date = entity.target_date
        model.created_at = entity.created_at
        model.updated_at = entity.updated_at
        model.deleted_at = entity.deleted_at
        return model

    @staticmethod
    def member_to_entity(model: StudyProblemMemberModel) -> StudyProblemMember:
        return StudyProblemMember(
            study_problem_member_id=StudyProblemMemberId(model.study_problem_member_id),
            study_problem_id=StudyProblemId(model.study_problem_id),
            user_account_id=UserAccountId(model.user_account_id),
            target_date=model.target_date,
            created_at=model.created_at,
            updated_at=model.updated_at,
            deleted_at=model.deleted_at,
        )
