"""UserActivity Mapper - 정규화된 테이블 구조 대응"""
from typing import Optional

from app.activity.domain.entity.user_activity import UserActivity
from app.activity.infra.mapper.tag_customization_mapper import TagCustomizationMapper
from app.activity.infra.mapper.user_problem_status_mapper import UserProblemStatusMapper
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.activity.infra.model.tag_custom import TagCustomModel
from app.common.domain.vo.identifiers import UserAccountId, UserActivityId


class UserActivityMapper:
    """UserActivity Aggregate Root <-> Models 변환

    정규화된 테이블 구조:
    - UserProblemStatusModel: 문제별 마스터 (banned_yn, solved_yn, representative_tag_id)
    - ProblemDateRecordModel: 날짜별 디테일 (marked_date, record_type, display_order)

    도메인 엔티티:
    - UserProblemStatus: 마스터 + date_records 리스트 포함
    """

    @staticmethod
    def to_entity(
        user_account_id: UserAccountId,
        user_activity_id: Optional[UserActivityId] = None,
        problem_status_models: Optional[list[UserProblemStatusModel]] = None,
        tag_custom_models: Optional[list[TagCustomModel]] = None,
    ) -> UserActivity:
        """Models -> UserActivity (Aggregate Root)"""
        problem_statuses = [
            UserProblemStatusMapper.status_to_entity(status_model)
            for status_model in (problem_status_models or [])
        ]

        tag_customizations = [
            TagCustomizationMapper.to_entity(model)
            for model in (tag_custom_models or [])
        ]

        return UserActivity(
            user_activity_id=user_activity_id,
            user_account_id=user_account_id,
            problem_statuses=problem_statuses,
            tag_customizations=tag_customizations,
        )
