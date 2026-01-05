"""유저 태그 목록 조회 Usecase"""

import logging

from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.common.domain.enums import SkillCode
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.recommendation.domain.repository.tag_skill_repository import TagSkillRepository
from app.tag.domain.repository.tag_repository import TagRepository
from app.tier.domain.repository.tier_repository import TierRepository
from app.user.application.command.get_user_tags_command import GetUserTagsCommand
from app.user.application.query.user_tags_query import (
    AccountStatQuery,
    CategoryQuery,
    NextLevelStatQuery,
    TagAliasQuery,
    UserTagDetailQuery,
    UserTagsQuery
)

logger = logging.getLogger(__name__)


class GetUserTagsUsecase:
    """유저 태그 목록 조회 Usecase"""

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        tag_repository: TagRepository,
        tag_skill_repository: TagSkillRepository,
        tier_repository: TierRepository
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.tag_repository = tag_repository
        self.tag_skill_repository = tag_skill_repository
        self.tier_repository = tier_repository

    @transactional
    async def execute(self, command: GetUserTagsCommand) -> UserTagsQuery:
        """
        유저 태그 목록 조회

        Args:
            command: 유저 태그 목록 조회 명령

        Returns:
            UserTagsQuery: 유저 태그 목록 정보
        """
        user_account_id = UserAccountId(command.user_account_id)

        # 1. 백준 계정 조회
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)
        if not bj_account:
            logger.error(f"[GetUserTagsUsecase] 백준 계정 연동 정보를 찾을 수 없음: {command.user_account_id}")
            raise APIException(ErrorCode.UNLINKED_USER)

        # 2. 태그별 통계 조회
        tag_stats = await self.baekjoon_account_repository.get_tag_stats(bj_account.bj_account_id)
        tag_stats_dict = {stat.tag_id.value: stat for stat in tag_stats}

        # 3. 모든 활성 태그 조회
        all_tags = await self.tag_repository.find_active_tags()

        # 4. 모든 활성 TagSkill 조회
        all_tag_skills = await self.tag_skill_repository.find_all_active()

        # TagSkill을 (tag_level, skill_code)로 매핑
        tag_skills_dict = {}
        for tag_skill in all_tag_skills:
            key = (tag_skill.tag_level, tag_skill.skill_code)
            tag_skills_dict[key] = tag_skill

        # 5. 태그별 상세 정보 생성
        tag_details = []
        for tag in all_tags:
            stat = tag_stats_dict.get(tag.tag_id.value)

            # 현재 레벨 계산
            current_level = self._calculate_current_level(stat, tag, tag_skills_dict)

            # accountStat 생성
            account_stat = self._create_account_stat(stat, current_level)

            # 다음 레벨 스탯 생성
            next_level_stat = self._create_next_level_stat(current_level, tag, tag_skills_dict)

            tag_detail = UserTagDetailQuery(
                tag_id=tag.tag_id.value,
                tag_code=tag.tag_code.value,
                tag_display_name=tag.display_name_ko,
                tag_targets=[],  # TODO: 목표 정보 추가
                tag_aliases=[TagAliasQuery(alias=alias.value) for alias in tag.aliases],
                required_stat=None,  # TODO: 선수 태그 정보 추가
                next_level_stat=next_level_stat,
                account_stat=account_stat,
                locked_yn=False,  # TODO: 잠금 여부 계산
                excluded_yn=False,  # TODO: 제외 여부 조회
                recommendation_yn=True  # TODO: 추천 여부 계산
            )
            tag_details.append(tag_detail)

        # 6. 카테고리별로 분류
        categories = self._categorize_tags(tag_details)

        return UserTagsQuery(
            categories=categories,
            tags=tag_details
        )

    def _calculate_current_level(self, stat, tag, tag_skills_dict) -> SkillCode:
        """현재 레벨 계산"""
        if not stat or stat.solved_problem_count == 0:
            return SkillCode.BEGINNER

        # MASTER 체크
        master_skill = tag_skills_dict.get((tag.tag_level, SkillCode.MASTER))
        if master_skill and self._meets_requirements(stat, master_skill):
            return SkillCode.MASTER

        # ADVANCED 체크
        advanced_skill = tag_skills_dict.get((tag.tag_level, SkillCode.ADVANCED))
        if advanced_skill and self._meets_requirements(stat, advanced_skill):
            return SkillCode.ADVANCED

        return SkillCode.BEGINNER

    def _meets_requirements(self, stat, tag_skill) -> bool:
        """TagSkill 요구사항 만족 여부"""
        if stat.solved_problem_count < tag_skill.requirements.min_solved_problem:
            return False

        if stat.highest_tier_id and stat.highest_tier_id.value < tag_skill.requirements.min_solved_problem_tier.value:
            return False

        return True

    def _create_account_stat(self, stat, current_level: SkillCode) -> AccountStatQuery:
        """유저 통계 생성"""
        if not stat:
            return AccountStatQuery(
                current_level=current_level.value,
                solved_problem_count=0,
                required_min_tier=None,
                higher_problem_tier=None,
                last_solved_date=None
            )

        # TODO: Tier 이름 조회하여 변환
        return AccountStatQuery(
            current_level=current_level.value,
            solved_problem_count=stat.solved_problem_count,
            required_min_tier=f"TIER_{stat.highest_tier_id.value}" if stat.highest_tier_id else None,
            higher_problem_tier=f"TIER_{stat.highest_tier_id.value}" if stat.highest_tier_id else None,
            last_solved_date=stat.last_solved_date
        )

    def _create_next_level_stat(self, current_level: SkillCode, tag, tag_skills_dict) -> NextLevelStatQuery | None:
        """다음 레벨 요구사항 생성"""
        next_level = None
        if current_level == SkillCode.BEGINNER:
            next_level = SkillCode.ADVANCED
        elif current_level == SkillCode.ADVANCED:
            next_level = SkillCode.MASTER
        else:
            return None  # 이미 MASTER

        next_skill = tag_skills_dict.get((tag.tag_level, next_level))
        if not next_skill:
            return None

        # TODO: Tier 이름 조회하여 변환
        return NextLevelStatQuery(
            next_level=next_level.value,
            solved_problem_count=next_skill.requirements.min_solved_problem,
            required_min_tier=f"TIER_{next_skill.requirements.min_user_tier.value}",
            higher_problem_tier=f"TIER_{next_skill.requirements.min_solved_problem_tier.value}"
        )

    def _categorize_tags(self, tag_details: list[UserTagDetailQuery]) -> list[CategoryQuery]:
        """태그를 카테고리별로 분류"""
        categories_dict = {}

        for tag in tag_details:
            level = tag.account_stat.current_level

            if level not in categories_dict:
                categories_dict[level] = []

            categories_dict[level].append(tag)

        # CategoryQuery 리스트 생성
        categories = [
            CategoryQuery(category_name=level, tags=tags)
            for level, tags in categories_dict.items()
        ]

        return categories
