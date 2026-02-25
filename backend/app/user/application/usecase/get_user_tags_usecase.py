"""유저 태그 목록 조회 Usecase"""

import logging
from typing import Dict, Tuple

from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.vo.tag_account_stat import TagAccountStat
from app.common.domain.enums import SkillCode
from app.common.domain.vo.identifiers import UserAccountId
from app.core.database import transactional
from app.core.error_codes import ErrorCode
from app.core.exception import APIException
from app.recommendation.domain.entity.tag_skill import TagSkill
from app.recommendation.domain.repository.tag_skill_repository import TagSkillRepository
from app.tag.domain.entity.tag import Tag
from app.tag.domain.repository.tag_repository import TagRepository
from app.tier.domain.entity.tier import Tier
from app.tier.domain.repository.tier_repository import TierRepository
from app.user.application.command.get_user_tags_command import GetUserTagsCommand
from app.user.application.query.user_tags_query import (
    AccountStatQuery,
    CategoryQuery,
    NextLevelStatQuery,
    PrevTagQuery,
    RequiredStatQuery,
    TagAliasQuery,
    TargetQuery,
    UserTagDetailQuery,
    UserTagsQuery,
)

logger = logging.getLogger(__name__)


class GetUserTagsUsecase:
    """유저 태그 목록 조회 Usecase"""

    _skill_code_full_names = {
        SkillCode.IM: "INTERMEDIATE",
        SkillCode.AD: "ADVANCED",
        SkillCode.MAS: "MASTER",
    }

    def __init__(
        self,
        baekjoon_account_repository: BaekjoonAccountRepository,
        tag_repository: TagRepository,
        tag_skill_repository: TagSkillRepository,
        tier_repository: TierRepository,
        activity_repository: UserActivityRepository
    ):
        self.baekjoon_account_repository = baekjoon_account_repository
        self.tag_repository = tag_repository
        self.tag_skill_repository = tag_skill_repository
        self.tier_repository = tier_repository
        self.activity_repository = activity_repository

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

        # 2. 모든 데이터 미리 조회
        # user_account_id를 전달하여 streak이 없을 때 problem_record 날짜 사용
        tag_stats = await self.baekjoon_account_repository.get_tag_stats(
            bj_account.bj_account_id,
            user_account_id
        )
        all_tags = await self.tag_repository.find_active_tags_with_relations()
        all_tag_skills = await self.tag_skill_repository.find_all_active()
        all_tiers = await self.tier_repository.find_all()
        activity: UserActivity = await self.activity_repository.find_only_tag_custom_by_user_account_id(user_account_id)

        # 3. 데이터 가공 및 매핑 생성
        tag_stats_dict: dict[int, TagAccountStat] = {stat.tag_id.value: stat for stat in tag_stats}
        all_tags_dict: dict[int, Tag] = {tag.tag_id.value: tag for tag in all_tags if tag.tag_id}
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill] = {
            (ts.tag_id.value, ts.skill_code): ts for ts in all_tag_skills if ts.tag_id
        }
        tiers_dict: dict[int, Tier] = {tier.tier_id.value: tier for tier in all_tiers if tier.tier_id}

        # 4. 태그별 상세 정보 생성
        tag_details: list[UserTagDetailQuery] = []
        for tag in all_tags:
            if not tag.tag_id:
                continue

            stat: TagAccountStat | None = tag_stats_dict.get(tag.tag_id.value)
            current_level = self._calculate_current_level(stat, tag, tag_skills_dict)
            
            # 선수 태그 및 locked_yn 계산 (parent_tag_relations 사용)
            locked_yn = False
            prev_tags_queries = []
            if tag.parent_tag_relations: # Use parent_tag_relations for prerequisites
                for parent_tag_relation in tag.parent_tag_relations:
                    # parent_tag_relation.leading_tag_id is the ID of the actual prerequisite tag
                    parent_tag = all_tags_dict.get(parent_tag_relation.leading_tag_id.value)
                    if not parent_tag or not parent_tag.tag_id:
                        continue
                    
                    parent_tag_stat = tag_stats_dict.get(parent_tag.tag_id.value)
                    satisfied_yn = parent_tag_stat is not None and parent_tag_stat.solved_problem_count > 0
                    
                    if not satisfied_yn:
                        locked_yn = True
                    
                    prev_tags_queries.append(
                        PrevTagQuery(
                            tag_id=parent_tag.tag_id.value,
                            tag_code=parent_tag.code,
                            tag_display_name=parent_tag.tag_display_name,
                            satisfied_yn=satisfied_yn,
                        )
                    )
            
            # required_stat 생성 (선수 태그 유무와 상관없이 항상 생성)
            # tag_skill의 IM(INTERMEDIATE) 레벨에서 min_user_tier 기준을 가져옴
            im_skill = tag_skills_dict.get((tag.tag_id.value, SkillCode.IM))
            min_tier_value = None
            if im_skill and im_skill.requirements.min_user_tier:
                min_tier_value = im_skill.requirements.min_user_tier.value

            required_stat_query = RequiredStatQuery(
                required_min_tier=min_tier_value,
                prev_tags=prev_tags_queries
            )

            # recommendation_yn 계산
            if tag.tag_id in activity.excluded_tag_ids:
                excluded_yn = True
            else:
                excluded_yn = False
            recommendation_yn = not (excluded_yn or locked_yn)

            # DTO 생성
            account_stat = self._create_account_stat(stat, current_level, tiers_dict, bj_account.current_tier_id.value)
            next_level_stat = self._create_next_level_stat(current_level, tag, tag_skills_dict, tiers_dict)
            
            # Fix alias query: tag.aliases is list[str], not list[dict]
            alias_queries = [TagAliasQuery(alias=alias['alias']) for alias in tag.aliases]

            # tag.targets로 직접 접근 (relationship으로 이미 매핑됨)
            target_queries = [
                TargetQuery(
                    target_id=target.target_id.value,
                    target_code=target.code,
                    target_display_name=target.display_name,
                )
                for target in tag.targets
                if target.target_id is not None
            ]

            tag_details.append(UserTagDetailQuery(
                tag_id=tag.tag_id.value,
                tag_code=tag.code,
                tag_display_name=tag.tag_display_name,
                tag_targets=target_queries,
                tag_aliases=alias_queries,
                required_stat=required_stat_query,
                next_level_stat=next_level_stat,
                account_stat=account_stat,
                locked_yn=locked_yn,
                excluded_yn=excluded_yn,
                recommendation_yn=recommendation_yn,
            ))

        # 5. 카테고리별로 분류
        categories = self._categorize_tags(tag_details)

        return UserTagsQuery(categories=categories, tags=tag_details)

    def _calculate_current_level(
        self,
        stat: TagAccountStat | None,
        tag: Tag,
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill],
    ) -> SkillCode:
        """현재 레벨 계산"""
        if not stat or stat.solved_problem_count == 0:
            return SkillCode.IM

        tag_id_val = tag.tag_id.value

        # MASTER 체크
        master_skill = tag_skills_dict.get((tag_id_val, SkillCode.MAS))
        if master_skill and self._meets_requirements(stat, master_skill):
            return SkillCode.MAS

        # ADVANCED 체크
        advanced_skill = tag_skills_dict.get((tag_id_val, SkillCode.AD))
        if advanced_skill and self._meets_requirements(stat, advanced_skill):
            return SkillCode.AD

        return SkillCode.IM

    def _meets_requirements(self, stat: TagAccountStat, tag_skill: TagSkill) -> bool:
        """TagSkill 요구사항 만족 여부"""
        if stat.solved_problem_count < tag_skill.requirements.min_solved_problem:
            return False

        min_tier = tag_skill.requirements.min_solved_problem_tier
        if stat.highest_tier_id and stat.highest_tier_id.value < min_tier.value:
            return False

        return True

    def _create_account_stat(
        self,
        stat: TagAccountStat | None,
        current_level: SkillCode,
        tiers_dict: dict[int, Tier],
        user_current_tier_id: int
    ) -> AccountStatQuery:
        """유저 통계 생성"""
        if not stat:
            return AccountStatQuery(
                current_level=self._skill_code_full_names.get(current_level, current_level.value),
                solved_problem_count=0,
                required_min_tier=user_current_tier_id,
                higher_problem_tier=None,
                last_solved_date=None,
            )
        
        # Use tier_id.value as string as requested by the user
        highest_tier_id_str = str(stat.highest_tier_id.value) if stat.highest_tier_id else None

        return AccountStatQuery(
            current_level=self._skill_code_full_names.get(current_level, current_level.value),
            solved_problem_count=stat.solved_problem_count,
            required_min_tier=user_current_tier_id,
            higher_problem_tier=highest_tier_id_str,
            last_solved_date=stat.last_solved_date,
        )

    def _create_next_level_stat(
        self,
        current_level: SkillCode,
        tag: Tag,
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill],
        tiers_dict: dict[int, Tier],
    ) -> NextLevelStatQuery | None:
        """다음 레벨 요구사항 생성"""
        next_level_code = None
        if current_level == SkillCode.IM:
            next_level_code = SkillCode.AD
        elif current_level == SkillCode.AD:
            next_level_code = SkillCode.MAS
        elif current_level == SkillCode.MAS: # If current is MAS, show MAS level requirements
            next_level_code = SkillCode.MAS
        else:
            return None # Should not happen unless SkillCode has more levels

        next_skill = tag_skills_dict.get((tag.tag_id.value, next_level_code))
        if not next_skill:
            return None
        
        reqs = next_skill.requirements
        # Use tier_id.value as string as requested by the user
        min_user_tier_id_str = str(reqs.min_user_tier.value) if reqs.min_user_tier else None
        min_solved_tier_id_str = str(reqs.min_solved_problem_tier.value) if reqs.min_solved_problem_tier else None

        return NextLevelStatQuery(
            next_level=self._skill_code_full_names.get(next_level_code, next_level_code.value),
            solved_problem_count=reqs.min_solved_problem,
            required_min_tier=min_user_tier_id_str,
            higher_problem_tier=min_solved_tier_id_str,
        )

    def _categorize_tags(self, tag_details: list[UserTagDetailQuery]) -> list[CategoryQuery]:
        """태그를 카테고리별로 분류"""
        categories_dict: dict[str, list[UserTagDetailQuery]] = {}
 
        categories_dict["EXCLUDED"] = []
        categories_dict["LOCKED"] = []
        
        for tag in tag_details:
            if tag.excluded_yn:
                categories_dict["EXCLUDED"].append(tag)
                continue
            
            if tag.locked_yn:
                categories_dict["LOCKED"].append(tag)
                continue
            
            key = tag.account_stat.current_level
                
            if key not in categories_dict:
                categories_dict[key] = []    
            categories_dict[key].append(tag)

        return [
            CategoryQuery(category_name=key, tags=tags)
            for key, tags in categories_dict.items()
        ]