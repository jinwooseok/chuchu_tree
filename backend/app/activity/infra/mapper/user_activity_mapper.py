"""UserActivity Mapper - 정규화된 테이블 구조 대응"""
from typing import Optional

from app.activity.domain.entity.user_activity import UserActivity
from app.activity.infra.mapper.problem_record_mapper import ProblemRecordMapper
from app.activity.infra.mapper.tag_customization_mapper import TagCustomizationMapper
from app.activity.infra.model.user_problem_status import UserProblemStatusModel
from app.activity.infra.model.problem_date_record import RecordType
from app.activity.infra.model.tag_custom import TagCustomModel
from app.common.domain.vo.identifiers import UserAccountId, UserActivityId


class UserActivityMapper:
    """UserActivity Entity <-> Models 변환

    정규화된 테이블 구조:
    - UserProblemStatusModel: 문제별 마스터 (banned_yn, solved_yn, representative_tag_id)
    - ProblemDateRecordModel: 날짜별 디테일 (marked_date, record_type, display_order)

    도메인 엔티티 매핑:
    - SOLVED: solved_yn=true + record_type='SOLVED' -> ProblemRecord
    - WILL_SOLVE: solved_yn=false, banned_yn=false + record_type='WILL_SOLVE' -> WillSolveProblem
    - BANNED: banned_yn=true (날짜 레코드 없음) -> ProblemBannedRecord
    """

    @staticmethod
    def to_entity(
        user_account_id: UserAccountId,
        user_activity_id: Optional[UserActivityId] = None,
        problem_status_models: Optional[list[UserProblemStatusModel]] = None,
        tag_custom_models: Optional[list[TagCustomModel]] = None,
    ) -> UserActivity:
        """Models -> Entity (Aggregate Root)

        Args:
            user_account_id: 유저 계정 ID
            user_activity_id: 활동 ID (선택)
            problem_status_models: UserProblemStatus 모델 목록 (date_records relationship 로드됨)
            tag_custom_models: TagCustom 모델 목록
        """
        will_solve_problems = []
        banned_problems = []
        solved_problems = []

        if problem_status_models:
            for status in problem_status_models:
                if status.banned_yn:
                    # BANNED 상태 - 날짜 레코드 없이 status만 사용
                    banned_problems.append(ProblemRecordMapper.to_banned_entity(status))
                elif status.date_records:
                    # 날짜 레코드가 있는 경우
                    for date_record in status.date_records:
                        if date_record.deleted_at is not None:
                            continue

                        if date_record.record_type == RecordType.SOLVED:
                            # SOLVED 상태
                            solved_problems.append(
                                ProblemRecordMapper.to_entity(status, date_record)
                            )
                        elif date_record.record_type == RecordType.WILL_SOLVE:
                            # WILL_SOLVE 상태
                            will_solve_problems.append(
                                ProblemRecordMapper.to_will_solve_entity(status, date_record)
                            )

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
