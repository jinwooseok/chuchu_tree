"""UserActivity Mapper"""
from typing import Optional

from app.activity.domain.entity.problem_banned_record import ProblemBannedRecord
from app.activity.domain.entity.problem_record import ProblemRecord
from app.activity.domain.entity.tag_customization import TagCustomization
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.entity.will_solve_problem import WillSolveProblem
from app.activity.infra.mapper.problem_banned_record_mapper import ProblemBannedRecordMapper
from app.activity.infra.mapper.problem_record_mapper import ProblemRecordMapper
from app.activity.infra.mapper.tag_customization_mapper import TagCustomizationMapper
from app.activity.infra.mapper.will_solve_problem_mapper import WillSolveProblemMapper
from app.activity.infra.model.problem_banned_record import ProblemBannedRecordModel
from app.activity.infra.model.problem_record import ProblemRecordModel
from app.activity.infra.model.tag_custom import TagCustomModel
from app.activity.infra.model.will_solve_problem import WillSolveProblemModel
from app.common.domain.vo.identifiers import UserAccountId, UserActivityId


class UserActivityMapper:
    """UserActivity Entity <-> Models 변환"""

    @staticmethod
    def to_entity(
        user_account_id: UserAccountId,
        user_activity_id: Optional[UserActivityId] = None, # UserActivityId는 있을 수도 있고 없을 수도 있음
        will_solve_problem_models: Optional[list[WillSolveProblemModel]] = None,
        problem_banned_record_models: Optional[list[ProblemBannedRecordModel]] = None,
        problem_record_models: Optional[Optional[list[ProblemRecordModel]]] = None,
        tag_custom_models: Optional[list[TagCustomModel]] = None,
    ) -> UserActivity:
        """Models -> Entity (Aggregate Root)"""

        will_solve_problems = [
            WillSolveProblemMapper.to_entity(model)
            for model in will_solve_problem_models
        ] if will_solve_problem_models else []

        banned_problems = [
            ProblemBannedRecordMapper.to_entity(model)
            for model in problem_banned_record_models
        ] if problem_banned_record_models else []

        solved_problems = [
            ProblemRecordMapper.to_entity(model)
            for model in problem_record_models
        ] if problem_record_models else []

        tag_customizations = [
            TagCustomizationMapper.to_entity(model)
            for model in tag_custom_models
        ] if tag_custom_models else []

        return UserActivity(
            user_activity_id=user_activity_id,
            user_account_id=user_account_id,
            will_solve_problems=will_solve_problems,
            banned_problems=banned_problems,
            solved_problems=solved_problems,
            tag_customizations=tag_customizations,
        )
