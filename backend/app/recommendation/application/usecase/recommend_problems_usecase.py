from datetime import datetime
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.vo.tag_account_stat import TagAccountStat
from app.common.domain.enums import FilterCode, TagLevel
from app.common.domain.vo.collections import TagIdSet
from app.common.domain.vo.identifiers import BaekjoonAccountId, TagId, TierId, UserAccountId
from app.common.domain.vo.primitives import TierRange
from app.core.database import transactional
from app.problem.domain.repository.problem_repository import ProblemRepository
from app.recommendation.application.query.recommend_problems_query import (
    RecommendProblemsQuery,
    RecommendedProblemQuery,
    RecommendReasonQuery,
    TagInfoQuery,
    TagAliasQuery,
    TagTargetQuery
)
from app.recommendation.domain.entity.level_filter import LevelFilter
from app.recommendation.domain.entity.tag_skill import TagSkill
from app.recommendation.domain.repository.level_filter_repository import LevelFilterRepository
from app.recommendation.domain.repository.tag_skill_repository import TagSkillRepository
from app.recommendation.domain.vo.recommendation_candidate import RecommendationCandidate
from app.recommendation.domain.vo.tag_candidate import TagCandidate, TagCandidates, TagStatsMap
from app.tag.domain.entity.tag import Tag
from app.tag.domain.repository.tag_repository import TagRepository
from app.tier.domain.repository.tier_repository import TierRepository
from app.user.domain.repository.user_account_repository import UserAccountRepository


class RecommendProblemsUsecase:
    def __init__(self,
                 user_account_repository: UserAccountRepository,
                 baekjoon_account_repository: BaekjoonAccountRepository,
                 user_activity_repository: UserActivityRepository,
                 tag_repository: TagRepository,
                 tag_skill_repository: TagSkillRepository,
                 recommend_filter_repository: LevelFilterRepository,
                 problem_repository: ProblemRepository,
                 tier_repository: TierRepository
                ):
        self.user_account_repository = user_account_repository
        self.baekjoon_account_repository = baekjoon_account_repository
        self.user_activity_repository = user_activity_repository
        self.tag_repository = tag_repository
        self.tag_skill_repository = tag_skill_repository
        self.recommend_filter_repository = recommend_filter_repository
        self.problem_repository = problem_repository
        self.tier_repository = tier_repository
    
    @transactional
    async def execute(
        self,
        user_account_id: UserAccountId,
        level_filter_codes: list[FilterCode] | None = None,
        tag_filter_codes: list[str] | None = None,
        count: int = 3
    ) -> RecommendProblemsQuery:
        # 1. 초기 데이터 로딩
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)
        raw_tag_stats = await self.baekjoon_account_repository.get_tag_stats(bj_account.bj_account_id)
        user_activity: UserActivity = await self.user_activity_repository.find_by_user_account_id(user_account_id)
        all_tags: list[Tag] = await self.tag_repository.find_active_tags_with_relations()
        all_tag_skills = await self.tag_skill_repository.find_all_active()

        # 2. 데이터 구조화 (O(1) 조회를 위해)
        stats_map: TagStatsMap = TagStatsMap.from_stats(raw_tag_stats)
        excluded_tag_ids: TagIdSet = user_activity.excluded_tag_ids
        all_tags_dict: dict[int, Tag] = {tag.tag_id.value: tag for tag in all_tags if tag.tag_id}

        # 3. 태그 후보 필터링 및 스코어링
        candidates_list: list[TagCandidate] = []
        for tag in all_tags:
            # (1) BAN 및 유저 필터 제외
            # 제외된 태그는 메인 추천 태그로 사용하지 않음
            # 단, 문제가 여러 태그를 가질 수 있으므로, 제외된 태그가 포함된 문제도 다른 태그를 통해 추천 가능
            if tag.tag_id in excluded_tag_ids: continue
            if tag_filter_codes and tag.code not in tag_filter_codes: continue

            # (2) 선수 태그 조건 검사
            if not self._is_pre_requisite_satisfied(tag, stats_map, bj_account.current_tier_id, all_tag_skills):
                continue

            # (3) 스코어 계산을 위한 Stat 보정 (기록 없는 태그 포함)
            stat = stats_map.get_or_empty(tag.tag_id)
            score = self._calculate_tag_score(stat, user_activity, all_tag_skills, bj_account.current_tier_id)
            candidates_list.append(TagCandidate.create(tag, stat, score))
        
        # 4. 가중치 랜덤 샘플링 (다양성 확보)
        # 점수가 높을수록 선택 확률이 높지만, 낮은 점수도 선택 가능
        all_candidates: TagCandidates = TagCandidates.from_list(candidates_list)

        # 랜덤 샘플링으로 상위 N개 선택 (추천할 개수보다 많이 선택)
        # 실제 추천은 3개지만, 문제를 찾지 못할 수 있으므로 여유있게 선택
        CANDIDATE_POOL_SIZE = 10  # 상위 10개 후보 선택
        tag_candidates: TagCandidates = all_candidates.weighted_random_sample(CANDIDATE_POOL_SIZE)

        # 5. 메인 추출 루프
        recommended_results: list[RecommendationCandidate] = []

        current_filter_code = level_filter_codes[0] if len(level_filter_codes) != 0 else FilterCode.NORMAL
        # print(current_filter_code)
        for tag_candidate in tag_candidates:
            if len(recommended_results) >= count: break

            criteria = await self._get_search_criteria(
                user_tier=bj_account.current_tier_id,
                tag_stat=tag_candidate.stat,
                filter_code=current_filter_code,
                all_skills=all_tag_skills
            )

            if not criteria: continue
            tier_range, min_skill_rate, max_skill_rate = criteria
        
            # WillSolve(찜한 문제) 우선 검색 로직 추가
            excluded_problem_ids = user_activity.solved_problem_ids | user_activity.banned_problem_ids
            problem = await self.problem_repository.find_recommended_problem(
                tag_id=tag_candidate.tag.tag_id,
                tier_range=tier_range,
                min_skill_rate=min_skill_rate,
                max_skill_rate=max_skill_rate,
                min_solved_count=tag.min_solved_person_count,
                exclude_ids=excluded_problem_ids,
                priority_ids=user_activity.will_solve_problem_ids # 찜한 문제 우선순위
            )
            print("추천된 문제 :" , problem)
            if problem:
                reasons = self._generate_reasons(
                    tag_candidate.stat,
                    tag_candidate.tag.tag_display_name,
                    all_tag_skills,
                    bj_account.current_tier_id,
                    current_filter_code
                )
                recommendation = RecommendationCandidate.create(
                    problem=problem,
                    reasons=reasons,
                    tag_name=tag_candidate.tag.tag_display_name
                )
                recommended_results.append(recommendation)

        # 6. Query 객체로 변환
        problem_queries = []
        for candidate in recommended_results:
            # 6-1. Tier 정보 조회
            tier = await self.tier_repository.find_by_level(candidate.problem.tier_level.value)
            tier_name = tier.tier_code if tier else "Unknown"

            # 6-2. Tag 정보 조회
            tag_infos = []
            for problem_tag in candidate.problem.tags:
                tag = all_tags_dict.get(problem_tag.tag_id.value)
                if tag:
                    # tag.targets로 직접 접근 (relationship으로 이미 매핑됨)
                    tag_targets = [
                        TagTargetQuery(
                            target_id=target.target_id.value,
                            target_code=target.code,
                            target_display_name=target.display_name
                        )
                        for target in tag.targets
                        if target.target_id is not None
                    ]

                    # Tag 별칭 정보
                    tag_aliases = [TagAliasQuery(alias=alias['alias']) for alias in tag.aliases]

                    tag_infos.append(TagInfoQuery(
                        tag_id=tag.tag_id.value,
                        tag_code=tag.code,
                        tag_display_name=tag.tag_display_name,
                        tag_target=tag_targets if tag_targets else None,
                        tag_aliases=tag_aliases
                    ))

            # 6-3. RecommendedProblemQuery 생성
            problem_query = RecommendedProblemQuery(
                problem_id=candidate.problem.problem_id.value,
                problem_title=candidate.problem.title,
                problem_tier_level=candidate.problem.tier_level.value,
                problem_tier_name=tier_name,
                problem_class_level=candidate.problem.class_level if candidate.problem.class_level else 0,
                recommend_reasons=[
                    RecommendReasonQuery(reason=r, additional_data=None)
                    for r in candidate.reasons
                ],
                tags=tag_infos
            )
            problem_queries.append(problem_query)

        return RecommendProblemsQuery(problems=problem_queries)

    async def _get_search_criteria(
        self,
        user_tier: TierId,
        tag_stat: TagAccountStat,
        filter_code: FilterCode,
        all_skills: list[TagSkill]
    ) -> tuple[TierRange, int] | None:
        """숙련도 판별 및 필터 엔티티를 통한 검색 조건 도출"""
        # 1. 숙련도 매칭
        current_skill = self._match_tag_skill(tag_stat, user_tier, all_skills)
        if not current_skill: return None

        # 2. 레벨 필터 엔티티 조회
        level_filter: LevelFilter = await self.recommend_filter_repository.find_by_skill_and_code(
            filter_code=filter_code.value,
            tag_skill_level=current_skill.skill_code.value
        )
        
        # print("level_filter :", level_filter)
        if not level_filter: return None

        # 3. 도메인 로직 호출 (TierRange 계산)
        tier_range = level_filter.calculate_tier_range(user_tier)

        # 4. Extreme 예외 보정 (H+2 조건)
        if filter_code == FilterCode.EXTREME:
            highest_val = tag_stat.highest_tier_id.value if tag_stat.highest_tier_id else 0
            min_val = max(tier_range.min_tier_id.value if tier_range.min_tier_id else 0, highest_val + 2)
            tier_range = TierRange(min_tier_id=TierId(min_val), max_tier_id=TierId(31))
        
        return tier_range, level_filter.min_tag_skill_rate, level_filter.max_tag_skill_rate

    def _match_tag_skill(self, tag_stat: TagAccountStat, user_tier: TierId, all_skills: list[TagSkill]) -> TagSkill | None:
        """요구사항 비교를 통한 숙련도 판별 (Entity 정책 활용)"""
        # 높은 숙련도부터 검사
        sorted_skills: list[TagSkill] = sorted(all_skills, key=lambda x: x.tag_skill_id.value, reverse=True)

        for skill in sorted_skills:
            req = skill.requirements
            highest_tier_val = tag_stat.highest_tier_id.value if tag_stat.highest_tier_id else 0
            if (tag_stat.solved_problem_count >= req.min_solved_problem and
                user_tier.value >= req.min_user_tier.value and
                highest_tier_val >= req.min_solved_problem_tier.value):
                return skill
        return sorted_skills[-1] if sorted_skills else None

    def _generate_reasons(
        self,
        tag_stat: TagAccountStat,
        tag_name: str,
        all_tag_skills: list[TagSkill],
        user_tier: TierId,
        filter_code: FilterCode
    ) -> list[str]:
        """추천 사유 생성기 (여러 개 반환)"""
        reasons = []

        # 1. 처음 푸는 태그 체크 (solved_problem_count로 정확히 확인)
        if tag_stat.solved_problem_count == 0:
            reasons.append(f"새로운 '{tag_name}' 분야에 도전해보세요!")
            return reasons  # 첫 문제는 다른 조건 의미 없음

        # 2. last_solved_date가 None인 경우 (서비스 가입 전에 푼 문제들)
        # solved_problem_count > 0인데 last_solved_date가 None
        # → 서비스 가입 전 기록이라 날짜를 알 수 없음
        # → 복습 주기 체크는 불가능하지만, 승급 임박은 확인 가능
        if not tag_stat.last_solved_date:
            # 승급 임박 체크만 수행
            level_up_info = self._check_level_up_status(tag_stat, user_tier, all_tag_skills)
            if level_up_info:
                reasons.append(level_up_info)

            # 승급 임박이 아니면 기본 메시지
            if not reasons:
                reasons.append(f"'{tag_name}' 숙련도를 높여보세요!")

            return reasons

        # 3. 복습 주기 체크 (날짜 정보가 있는 경우)
        days_diff = (datetime.now().date() - tag_stat.last_solved_date).days

        # 현재 숙련도를 찾아서 해당 숙련도의 추천 주기를 가져옴
        current_skill = self._match_tag_skill(tag_stat, user_tier, all_tag_skills)
        if current_skill and days_diff >= current_skill.recommendation_period:
            reasons.append(f"'{tag_name}' 태그를 안 푼 지 {days_diff}일이 지났어요.")

        # 4. 승급 임박 체크
        level_up_info = self._check_level_up_status(tag_stat, user_tier, all_tag_skills)
        if level_up_info:
            reasons.append(level_up_info)

        # 5. 기본 메시지 (사유가 없을 때만)
        if not reasons:
            reasons.append(f"'{tag_name}' 숙련도를 높일 시간입니다.")

        return reasons

    def _check_level_up_status(
        self,
        tag_stat: TagAccountStat,
        user_tier: TierId,
        all_tag_skills: list[TagSkill]
    ) -> str | None:
        """승급 임박 상태 확인 및 메시지 생성"""
        current_skill = self._match_tag_skill(tag_stat, user_tier, all_tag_skills)
        if not current_skill:
            return None

        sorted_skills = sorted(all_tag_skills, key=lambda x: x.tag_skill_id.value)
        current_index = next((i for i, s in enumerate(sorted_skills) if s.tag_skill_id == current_skill.tag_skill_id), -1)

        if current_index == -1 or current_index >= len(sorted_skills) - 1:
            return None

        next_skill = sorted_skills[current_index + 1]
        current_solved = tag_stat.solved_problem_count
        required_solved = next_skill.requirements.min_solved_problem
        problems_needed = required_solved - current_solved

        if 0 < problems_needed < 5:
            skill_name = next_skill.skill_code.value
            return f"{problems_needed}문제만 더 풀면 {skill_name} 달성!"

        return None
    
    def _is_pre_requisite_satisfied(
        self,
        tag: Tag,
        stats_map: TagStatsMap,
        user_tier: TierId,
        all_tag_skills: list[TagSkill]
    ) -> bool:
        """선수 태그 조건을 만족하는지 확인"""
        if not tag.parent_tag_relations:
            return True
        for relation in tag.parent_tag_relations:
            parent_stat = stats_map.get(relation.leading_tag_id)
            if not parent_stat:
                return False

        # 선수 태그의 숙련도를 계산
        parent_skill = self._match_tag_skill(parent_stat, user_tier, all_tag_skills)

        # 예: 선수 태그가 최소 'BEGINNER' 이상이어야 함
        return parent_skill and parent_skill.tag_level >= TagLevel.BEGINNER
    
    def _calculate_tag_score(
        self,
        tag_stat: TagAccountStat,
        user_activity: UserActivity,
        all_tag_skills: list[TagSkill],
        user_tier: TierId
    ) -> float:
        """태그별 추천 우선순위 점수 계산"""
        score = 0.0

        # 1. 복습 주기 점수 (오래될수록 가중치, 최대 50점)
        if tag_stat.last_solved_date:
            days_diff = (datetime.now().date() - tag_stat.last_solved_date).days

            # 현재 숙련도를 찾아서 해당 숙련도의 추천 주기를 기준으로 점수 계산
            current_skill = self._match_tag_skill(tag_stat, user_tier, all_tag_skills)
            if current_skill:
                # recommendation_period를 넘긴 시점부터 점수 급증
                # 넘긴 일수에 비례하여 점수 추가 (최대 50점)
                if days_diff >= current_skill.recommendation_period:
                    excess_days = days_diff - current_skill.recommendation_period
                    score += min(excess_days * 2 + 10, 50)  # 기본 10점 + 초과일 * 2
            else:
                # 숙련도를 찾을 수 없는 경우 기본 로직
                score += min(days_diff * 2, 50)
        else:
            # 아예 처음 푸는 태그 또는 서비스 가입 전 기록
            if tag_stat.solved_problem_count == 0:
                # 처음 푸는 태그는 높은 우선순위 부여
                score += 40
            else:
                # 서비스 가입 전 기록은 중간 우선순위
                score += 20

        # 2. 승급 임박 가중치 (다음 레벨까지 5문제 미만일 때, +30점)
        level_up_bonus = self._calculate_level_up_bonus(tag_stat, user_tier, all_tag_skills)
        score += level_up_bonus

        # 3. 사용자 선호도 (찜한 문제가 있는 경우, +20점)
        # NOTE: 현재는 태그 정보가 없어서 간단하게 찜한 문제가 있으면 보너스
        if user_activity.will_solve_problem_ids:
            score += 20

        return score

    def _calculate_level_up_bonus(
        self,
        tag_stat: TagAccountStat,
        user_tier: TierId,
        all_tag_skills: list[TagSkill]
    ) -> float:
        """승급 임박 보너스 점수 계산"""
        # 현재 숙련도 찾기
        current_skill = self._match_tag_skill(tag_stat, user_tier, all_tag_skills)
        if not current_skill:
            return 0.0

        # 숙련도를 레벨 순으로 정렬 (낮은 레벨부터)
        sorted_skills = sorted(all_tag_skills, key=lambda x: x.tag_skill_id.value)

        # 다음 숙련도 찾기
        current_index = next((i for i, s in enumerate(sorted_skills) if s.tag_skill_id == current_skill.tag_skill_id), -1)
        if current_index == -1 or current_index >= len(sorted_skills) - 1:
            # 마지막 숙련도(MASTER)이거나 찾을 수 없으면 보너스 없음
            return 0.0

        next_skill = sorted_skills[current_index + 1]

        # 다음 레벨까지 필요한 문제 수
        current_solved = tag_stat.solved_problem_count
        required_solved = next_skill.requirements.min_solved_problem
        problems_needed = required_solved - current_solved

        # 5문제 미만 남았으면 30점 부여
        if 0 < problems_needed < 5:
            return 30.0

        return 0.0