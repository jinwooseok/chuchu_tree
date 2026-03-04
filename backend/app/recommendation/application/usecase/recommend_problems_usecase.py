from datetime import datetime
import random
from app.activity.domain.entity.user_activity import UserActivity
from app.activity.domain.repository.user_activity_repository import UserActivityRepository
from app.baekjoon.domain.repository.baekjoon_account_repository import BaekjoonAccountRepository
from app.baekjoon.domain.repository.problem_history_repository import ProblemHistoryRepository
from app.baekjoon.domain.vo.tag_account_stat import TagAccountStat
from app.common.domain.enums import FilterCode, SkillCode, TagLevel, ExclusionMode
from app.common.domain.vo.collections import ProblemIdSet, TagIdSet
from app.common.domain.vo.identifiers import BaekjoonAccountId, TagId, TargetId, TierId, UserAccountId
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
from app.recommendation.domain.vo.search_criteria import SearchCriteria
from app.recommendation.domain.vo.tag_candidate import TagCandidate, TagCandidates, TagStatsMap
from app.tag.domain.entity.tag import Tag
from app.tag.domain.repository.tag_repository import TagRepository
from app.target.domain.repository.target_repository import TargetRepository
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
                 tier_repository: TierRepository,
                 problem_history_repository: ProblemHistoryRepository,
                 target_repository: TargetRepository
                ):
        self.user_account_repository = user_account_repository
        self.baekjoon_account_repository = baekjoon_account_repository
        self.user_activity_repository = user_activity_repository
        self.tag_repository = tag_repository
        self.tag_skill_repository = tag_skill_repository
        self.recommend_filter_repository = recommend_filter_repository
        self.problem_repository = problem_repository
        self.tier_repository = tier_repository
        self.problem_history_repository = problem_history_repository
        self.target_repository = target_repository
        self.skill_name_map = {
            "AD": "ADVANCED",
            "MAS": "MASTER",
            "IM": "INTERMEDIATE"
        }
    
    @transactional(readonly=True)
    async def execute(
        self,
        user_account_id: UserAccountId,
        level_filter_codes: list[FilterCode] | None = None,
        tag_filter_codes: list[str] | None = None,
        count: int = 3,
        exclusion_mode: ExclusionMode = ExclusionMode.LENIENT,
        additional_excluded_problem_ids: set[int] | None = None,
    ) -> RecommendProblemsQuery:
        # 1. 초기 데이터 로딩
        bj_account = await self.baekjoon_account_repository.find_by_user_id(user_account_id)
        if bj_account is None:
            from app.core.error_codes import ErrorCode
            from app.core.exception import APIException
            raise APIException(ErrorCode.BAEKJOON_USER_NOT_FOUND)
        # user_account_id를 전달하여 streak이 없을 때 problem_record 날짜 사용
        raw_tag_stats = await self.baekjoon_account_repository.get_tag_stats(
            bj_account.bj_account_id,
            user_account_id
        )
        user_activity: UserActivity = await self.user_activity_repository.find_by_user_account_id(user_account_id)
        all_tags: list[Tag] = await self.tag_repository.find_active_tags_with_relations()
        all_tag_skills = await self.tag_skill_repository.find_all_active()
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill] = {
            (ts.tag_id.value, ts.skill_code): ts for ts in all_tag_skills if ts.tag_id
        }

        # 1-1. Fetch user account to get active target (Requirement 4)
        user_account = await self.user_account_repository.find_by_id(user_account_id)
        active_target_id = TargetId(value=3) # BEGINNER DEFAULT
        active_target_name = None
        if user_account and user_account.targets:
            active_user_target = user_account._get_current_target()
            if active_user_target:
                active_target_id = active_user_target.target_id
                # Fetch target display name
                target = await self.target_repository.find_by_id(active_target_id)
                if target:
                    active_target_name = target.display_name

        # 2. 데이터 구조화 (O(1) 조회를 위해)
        stats_map: TagStatsMap = TagStatsMap.from_stats(raw_tag_stats)
        excluded_tag_ids: TagIdSet = user_activity.excluded_tag_ids
        
        all_tags_dict: dict[int, Tag] = {}
        target_tag_ids = set()
        for tag in all_tags:
            if tag.tag_id:
                all_tags_dict[tag.tag_id.value] = tag
                if active_target_id and tag.targets and any(target.target_id.value == active_target_id.value for target in tag.targets):
                    target_tag_ids.add(tag.tag_id.value)

        # DEBUG: 타겟 태그 정보 출력
        if target_tag_ids:
            target_tag_names = [all_tags_dict.get(tid).tag_display_name for tid in target_tag_ids if all_tags_dict.get(tid)]
            print(f"[DEBUG TARGET] User has active target: {active_target_id}")
            print(f"[DEBUG TARGET] Target tag count: {len(target_tag_ids)}")
            print(f"[DEBUG TARGET] Target tags: {target_tag_names[:5]}...")  # 처음 5개만 표시

        # DEBUG: Excluded 태그 출력
        if excluded_tag_ids:
            excluded_tag_names = [all_tags_dict.get(tid.value).tag_display_name for tid in excluded_tag_ids if all_tags_dict.get(tid.value)]
            print(f"[DEBUG EXCLUDED] 제외된 태그 ({len(excluded_tag_ids)}개): {excluded_tag_names}")
            print(f"[DEBUG EXCLUDED] Exclusion Mode: {exclusion_mode.value}\n")

        # 3. 태그 후보 필터링 및 스코어링
        candidates_list: list[TagCandidate] = []
        for tag in all_tags:
            # (1) BAN 및 유저 필터 제외
            # 제외된 태그는 메인 추천 태그로 사용하지 않음
            # 단, 문제가 여러 태그를 가질 수 있으므로, 제외된 태그가 포함된 문제도 다른 태그를 통해 추천 가능
            if tag.tag_id in excluded_tag_ids: continue
            if tag_filter_codes and tag.code not in tag_filter_codes: continue

            # (2) 선수 태그 조건 검사
            if not self._is_pre_requisite_satisfied(tag, stats_map, bj_account.current_tier_id, tag_skills_dict):
                continue

            # (3) 스코어 계산을 위한 Stat 보정 (기록 없는 태그 포함)
            stat = stats_map.get_or_empty(tag.tag_id)
            score = self._calculate_tag_score(stat, user_activity, tag_skills_dict, bj_account.current_tier_id, target_tag_ids)

            # DEBUG: 타겟 가중치 확인
            if target_tag_ids and stat.tag_id.value in target_tag_ids:
                print(f"[DEBUG TARGET] Tag '{tag.tag_display_name}' (ID: {tag.tag_id.value}) matches target! Score: {score}")

            candidates_list.append(TagCandidate.create(tag, stat, score))
        
        # 4. 가중치 랜덤 샘플링 (다양성 확보)
        # 점수가 높을수록 선택 확률이 높지만, 낮은 점수도 선택 가능
        all_candidates: TagCandidates = TagCandidates.from_list(candidates_list)

        # DEBUG: 전체 후보 점수 출력 (상위 20개)
        sorted_candidates = sorted(candidates_list, key=lambda c: c.score, reverse=True)
        print("\n========== [DEBUG] 태그 점수 Top 20 ==========")
        for i, candidate in enumerate(sorted_candidates[:20], 1):
            target_marker = " 🎯 [TARGET]" if target_tag_ids and candidate.stat.tag_id.value in target_tag_ids else ""
            print(f"{i}. {candidate.tag.tag_display_name:20s} | Score: {candidate.score:6.1f}{target_marker}")
        print("=" * 50)

        # DEBUG: 상위 5개 점수 구성 자세히 보기
        print("\n========== [DEBUG] 점수 구성 (Top 5) ==========")
        for i, candidate in enumerate(sorted_candidates[:5], 1):
            # 점수 다시 계산해서 breakdown 얻기
            stat = candidate.stat

            # 복습 주기 점수
            review_score = 0.0
            if stat.last_solved_date:
                days_diff = (datetime.now().date() - stat.last_solved_date).days
                current_skill = self._match_tag_skill(stat, bj_account.current_tier_id, tag_skills_dict)
                if current_skill and days_diff >= current_skill.recommendation_period:
                    excess_days = days_diff - current_skill.recommendation_period
                    review_score = min(excess_days * 2 + 10, 50)
            else:
                review_score = 40 if stat.solved_problem_count == 0 else 20 # 풀었는데 기록이 없는 경우 20

            # 승급 임박
            level_up_bonus = self._calculate_level_up_bonus(stat, bj_account.current_tier_id, tag_skills_dict)

            # 타겟
            target_score = 30 if (target_tag_ids and stat.tag_id.value in target_tag_ids) else 0

            print(f"\n{i}. {candidate.tag.tag_display_name} (Total: {candidate.score:.1f})")
            print(f"   ├─ 복습주기: {review_score:.1f}점")
            print(f"   ├─ 승급임박: {level_up_bonus:.1f}점")
            print(f"   └─ 타겟:     {target_score:.1f}점")
        print("=" * 50 + "\n")

        # 4-1. Fetch actual solved problems from Baekjoon (Requirement 2 - 한 번만 조회)
        history_solved_ids_raw = await self.problem_history_repository.find_solved_ids_by_bj_account_id(
            bj_account.bj_account_id
        )
        history_solved_ids = ProblemIdSet.from_values(history_solved_ids_raw) if history_solved_ids_raw else ProblemIdSet.empty()

        # 5. 메인 추출 루프 - 가중치 랜덤 샘플링으로 count개 채우기
        recommended_results: list[RecommendationCandidate] = []
        recommended_problem_ids: set[int] = set()  # 이미 추천한 문제 ID 추적
        sampled_tags_log: list[tuple[str, bool]] = []  # 샘플링된 태그 로그 (태그명, 성공여부)
        failed_attempts = 0
        max_failed_attempts = count * 10  # 무한 루프 방지

        effective_filter_codes = level_filter_codes if len(level_filter_codes) != 0 else [FilterCode.NORMAL]
        display_filter_code = effective_filter_codes[0]  # 표시 목적용

        while len(recommended_results) < count and failed_attempts < max_failed_attempts:
            # 가중치 기반으로 태그 1개 랜덤 선택
            sampled = all_candidates.weighted_random_sample(1)
            if len(sampled) == 0:
                break

            tag_candidate = list(sampled)[0]

            criteria_list = await self._get_search_criteria_list(
                user_tier=bj_account.current_tier_id,
                tag_stat=tag_candidate.stat,
                filter_codes=effective_filter_codes,
                tag_skills_dict=tag_skills_dict
            )

            if not criteria_list:
                sampled_tags_log.append((tag_candidate.tag.tag_display_name, False))
                failed_attempts += 1
                continue

            # 태그 직접 지정 시 tier_range 무시 (skill rate만 사용)
            if tag_filter_codes:
                criteria_list = [
                    SearchCriteria(
                        tier_range=TierRange(min_tier_id=None, max_tier_id=None),
                        min_skill_rate=c.min_skill_rate,
                        max_skill_rate=c.max_skill_rate
                    )
                    for c in criteria_list
                ]

            # Merge all exclusion sources (Requirement 2: including problem_history)
            excluded_problem_ids_vo = (
                user_activity.solved_problem_ids |  # Manual tracking (ProblemRecord)
                user_activity.banned_problem_ids |  # Banned problems
                history_solved_ids                   # Actual Baekjoon solves
            )

            # Convert ProblemIdSet to set[int] for repository
            excluded_problem_ids = {pid.value for pid in excluded_problem_ids_vo}
            excluded_problem_ids |= recommended_problem_ids  # 이미 추천한 문제도 제외
            if additional_excluded_problem_ids:
                excluded_problem_ids |= additional_excluded_problem_ids

            problem = await self.problem_repository.find_recommended_problem(
                tag_id=tag_candidate.tag.tag_id,
                criteria_list=criteria_list,
                min_solved_count=tag_candidate.tag.min_solved_person_count,
                exclude_ids=excluded_problem_ids,
                priority_ids=set()
            )
            if problem:
                # Requirement 3: STRICT mode filtering
                if exclusion_mode == ExclusionMode.STRICT:
                    excluded_tag_ids_list = [TagId(tid.value) for tid in excluded_tag_ids]
                    if problem.has_any_tag(excluded_tag_ids_list):
                        problem_tag_names = [all_tags_dict.get(tag.tag_id.value).tag_display_name for tag in problem.tags if all_tags_dict.get(tag.tag_id.value)]
                        print(f"[DEBUG STRICT] ❌ 문제 {problem.problem_id.value} 제외됨 (excluded 태그 포함): {problem_tag_names}")
                        sampled_tags_log.append((tag_candidate.tag.tag_display_name, False))
                        failed_attempts += 1
                        continue  # Skip this problem, try next candidate

                reasons = self._generate_reasons(
                    tag_candidate.stat,
                    tag_candidate.tag.tag_display_name,
                    tag_skills_dict,
                    bj_account.current_tier_id,
                    display_filter_code,
                    target_tag_ids if isinstance(target_tag_ids, set) else set(),
                    active_target_name
                )
                recommendation = RecommendationCandidate.create(
                    problem=problem,
                    reasons=reasons,
                    tag_name=tag_candidate.tag.tag_display_name,
                    primary_tag_id=tag_candidate.tag.tag_id
                )
                recommended_results.append(recommendation)
                recommended_problem_ids.add(problem.problem_id.value)  # 중복 방지를 위해 추가
                sampled_tags_log.append((tag_candidate.tag.tag_display_name, True))
            else:
                sampled_tags_log.append((tag_candidate.tag.tag_display_name, False))
                failed_attempts += 1

        # DEBUG: 샘플링된 태그 순서 출력
        print("\n========== [DEBUG] 샘플링된 태그 순서 ==========")
        success_count = sum(1 for _, success in sampled_tags_log if success)
        print(f"총 샘플링 횟수: {len(sampled_tags_log)}회 (성공: {success_count}, 실패: {len(sampled_tags_log) - success_count})")
        for i, (tag_name, success) in enumerate(sampled_tags_log, 1):
            status = "✅" if success else "❌"
            print(f"{i}. {status} {tag_name}")
        print("=" * 50 + "\n")

        # DEBUG: 최종 추천 결과 출력
        print(f"\n========== [DEBUG] 최종 추천된 문제 (요청: {count}개, 실제: {len(recommended_results)}개) ==========")
        for i, rec in enumerate(recommended_results, 1):
            problem_tag_names = [all_tags_dict.get(tag.tag_id.value).tag_display_name for tag in rec.problem.tags if all_tags_dict.get(tag.tag_id.value)]
            print(f"{i}. [{rec.problem.problem_id.value}] {rec.problem.title}")
            print(f"   메인 태그: {rec.tag_name}")
            print(f"   전체 태그: {problem_tag_names}")
            print(f"   추천 이유: {rec.reasons[0] if rec.reasons else 'N/A'}")
        print("=" * 50 + "\n")

        # 6. Query 객체로 변환
        problem_queries = []
        for candidate in recommended_results:
            # 6-1. Tier 정보 조회
            tier = await self.tier_repository.find_by_level(candidate.problem.tier_level.value)
            tier_name = tier.tier_code if tier else "Unknown"

            # 6-2. Tag 정보 조회 및 정렬 (Requirement 1)
            tag_infos = []
            primary_tag_info = None
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

                    tag_info = TagInfoQuery(
                        tag_id=tag.tag_id.value,
                        tag_code=tag.code,
                        tag_display_name=tag.tag_display_name,
                        tag_targets=tag_targets if tag_targets else None,
                        tag_aliases=tag_aliases
                    )

                    # Check if this is the primary recommendation tag
                    if tag.tag_id.value == candidate.primary_tag_id.value:
                        primary_tag_info = tag_info
                    else:
                        tag_infos.append(tag_info)

            # Place primary tag first
            if primary_tag_info:
                tag_infos.insert(0, primary_tag_info)

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

    async def _get_search_criteria_list(
        self,
        user_tier: TierId,
        tag_stat: TagAccountStat,
        filter_codes: list[FilterCode],
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill]
    ) -> list[SearchCriteria]:
        """숙련도 판별 및 필터 엔티티를 통한 검색 조건 도출 (복수 레벨 지원)"""
        # 1. 숙련도 매칭
        current_skill = self._match_tag_skill(tag_stat, user_tier, tag_skills_dict)
        if not current_skill:
            return []

        # 2. 레벨 필터 엔티티 일괄 조회
        filter_code_values = [fc.value for fc in filter_codes]
        level_filters: list[LevelFilter] = await self.recommend_filter_repository.find_by_skill_and_codes(
            tag_skill_level=current_skill.skill_code.value,
            filter_codes=filter_code_values
        )

        if not level_filters:
            return []

        # 3. 각 필터별 독립적인 SearchCriteria 생성
        criteria_list: list[SearchCriteria] = []
        for level_filter in level_filters:
            tier_range = level_filter.calculate_tier_range(user_tier)

            # Extreme 예외 보정 (H+2 조건) - 해당 필터에만 적용
            if level_filter.filter_code == FilterCode.EXTREME:
                highest_val = tag_stat.highest_tier_id.value if tag_stat.highest_tier_id else 0
                min_val = max(tier_range.min_tier_id.value if tier_range.min_tier_id else 0, highest_val + 2)
                tier_range = TierRange(min_tier_id=TierId(min_val), max_tier_id=TierId(31))

            criteria_list.append(SearchCriteria(
                tier_range=tier_range,
                min_skill_rate=level_filter.min_tag_skill_rate,
                max_skill_rate=level_filter.max_tag_skill_rate
            ))

        return criteria_list

    def _match_tag_skill(self, tag_stat: TagAccountStat, user_tier: TierId, tag_skills_dict: dict[tuple[int, SkillCode], TagSkill]) -> TagSkill | None:
        """요구사항 비교를 통한 숙련도 판별 (해당 태그의 skill만 검사)"""
        tag_id_val = tag_stat.tag_id.value
        highest_tier_val = tag_stat.highest_tier_id.value if tag_stat.highest_tier_id else 0

        # 높은 숙련도부터 검사: MAS → AD → IM
        for skill_code in [SkillCode.MAS, SkillCode.AD, SkillCode.IM]:
            skill = tag_skills_dict.get((tag_id_val, skill_code))
            if not skill:
                continue
            req = skill.requirements
            if (tag_stat.solved_problem_count >= req.min_solved_problem and
                user_tier.value >= req.min_user_tier.value and
                highest_tier_val >= req.min_solved_problem_tier.value):
                return skill

        # 요구사항을 충족하지 못하면 IM 반환 (기본값)
        return tag_skills_dict.get((tag_id_val, SkillCode.IM))

    def _generate_reasons(
        self,
        tag_stat: TagAccountStat,
        tag_name: str,
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill],
        user_tier: TierId,
        filter_code: FilterCode,
        target_tag_ids: set[int] = None,
        target_display_name: str = None
    ) -> list[str]:
        """추천 사유 생성기 (여러 개 반환)"""
        reasons = []

        # 0. 타겟 태그 체크
        if target_tag_ids and tag_stat.tag_id.value in target_tag_ids:
            if target_display_name:
                reasons.append(f"{target_display_name} 목표에 잘 어울리는 문제입니다.")
            else:
                reasons.append(f"{tag_name}은(는) 현재 목표에 포함된 태그입니다!")

        # 1. 처음 푸는 태그 체크 (solved_problem_count로 정확히 확인)
        if tag_stat.solved_problem_count == 0:
            reasons.append(f"새로운 '{tag_name}' 분야에 도전해보세요!")
            if len(reasons) > 1:
                random.shuffle(reasons)
            return reasons  # 첫 문제는 다른 조건 의미 없음

        # 2. last_solved_date가 None인 경우 (서비스 가입 전에 푼 문제들)
        # solved_problem_count > 0인데 last_solved_date가 None
        # → 서비스 가입 전 기록이라 날짜를 알 수 없음
        # → 복습 주기 체크는 불가능하지만, 승급 임박은 확인 가능
        if not tag_stat.last_solved_date:
            # 승급 임박 체크만 수행
            level_up_info = self._check_level_up_status(tag_stat, user_tier, tag_skills_dict, tag_name)
            if level_up_info:
                reasons.append(level_up_info)

            # 승급 임박이 아니면 기본 메시지
            if not reasons:
                reasons.append(f"'{tag_name}' 숙련도를 높여보세요!")

            if len(reasons) > 1:
                random.shuffle(reasons)
            return reasons

        # 3. 복습 주기 체크 (날짜 정보가 있는 경우)
        days_diff = (datetime.now().date() - tag_stat.last_solved_date).days

        # 현재 숙련도를 찾아서 해당 숙련도의 추천 주기를 가져옴
        current_skill = self._match_tag_skill(tag_stat, user_tier, tag_skills_dict)
        if current_skill and days_diff >= current_skill.recommendation_period:
            reasons.append(f"'{tag_name}' 태그를 안 푼 지 {days_diff}일이 지났어요.")

        # 4. 승급 임박 체크
        level_up_info = self._check_level_up_status(tag_stat, user_tier, tag_skills_dict, tag_name)
        if level_up_info:
            reasons.append(level_up_info)

        # 5. 기본 메시지 (사유가 없을 때만)
        if not reasons:
            reasons.append(f"'{tag_name}' 숙련도를 높일 시간입니다.")

        if len(reasons) > 1:
            random.shuffle(reasons)
        return reasons

    _SKILL_CODE_ORDER = {SkillCode.IM: SkillCode.AD, SkillCode.AD: SkillCode.MAS}

    def _check_level_up_status(
        self,
        tag_stat: TagAccountStat,
        user_tier: TierId,
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill],
        tag_name: str
    ) -> str | None:
        """승급 임박 상태 확인 및 메시지 생성"""
        current_skill = self._match_tag_skill(tag_stat, user_tier, tag_skills_dict)
        if not current_skill:
            return None

        # 같은 태그 내에서 다음 숙련도 결정 (IM→AD, AD→MAS)
        next_skill_code = self._SKILL_CODE_ORDER.get(current_skill.skill_code)
        if not next_skill_code:
            return None

        next_skill = tag_skills_dict.get((tag_stat.tag_id.value, next_skill_code))
        if not next_skill:
            return None

        current_solved = tag_stat.solved_problem_count
        required_solved = next_skill.requirements.min_solved_problem
        problems_needed = required_solved - current_solved

        if 0 < problems_needed < 5:
            skill_code = next_skill.skill_code.value
            return f"'{tag_name}' {problems_needed}문제만 더 풀면 {self.skill_name_map[skill_code]} 달성!"

        return None
    
    def _is_pre_requisite_satisfied(
        self,
        tag: Tag,
        stats_map: TagStatsMap,
        user_tier: TierId,
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill]
    ) -> bool:
        """선수 태그 조건을 만족하는지 확인"""
        if not tag.parent_tag_relations:
            return True
        for relation in tag.parent_tag_relations:
            parent_stat = stats_map.get(relation.leading_tag_id)
            if not parent_stat:
                return False

        # 선수 태그의 숙련도를 계산
        parent_skill = self._match_tag_skill(parent_stat, user_tier, tag_skills_dict)

        # 예: 선수 태그가 최소 'BEGINNER' 이상이어야 함
        return parent_skill and parent_skill.tag_level >= TagLevel.BEGINNER
    
    def _calculate_tag_score(
        self,
        tag_stat: TagAccountStat,
        user_activity: UserActivity,
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill],
        user_tier: TierId,
        target_tag_ids: set[int]
    ) -> float:
        """태그별 추천 우선순위 점수 계산"""
        score = 0.0

        # 1. 복습 주기 점수 (오래될수록 가중치, 최대 50점)
        review_score = 0.0
        if tag_stat.last_solved_date:
            days_diff = (datetime.now().date() - tag_stat.last_solved_date).days

            # 현재 숙련도를 찾아서 해당 숙련도의 추천 주기를 기준으로 점수 계산
            current_skill = self._match_tag_skill(tag_stat, user_tier, tag_skills_dict)
            if current_skill:
                # recommendation_period를 넘긴 시점부터 점수 급증
                # 넘긴 일수에 비례하여 점수 추가 (최대 50점)
                if days_diff >= current_skill.recommendation_period:
                    excess_days = days_diff - current_skill.recommendation_period
                    review_score = min(excess_days * 2 + 10, 50)  # 기본 10점 + 초과일 * 2
            else:
                # 숙련도를 찾을 수 없는 경우 기본 로직
                review_score = min(days_diff * 2, 50)
        else:
            # 아예 처음 푸는 태그 또는 서비스 가입 전 기록
            if tag_stat.solved_problem_count == 0:
                # 처음 푸는 태그는 높은 우선순위 부여
                review_score = 40
            else:
                # 서비스 가입 전 기록은 중간 우선순위
                review_score = 20
        score += review_score

        # 2. 승급 임박 가중치 (다음 레벨까지 5문제 미만일 때, +30점)
        level_up_bonus = self._calculate_level_up_bonus(tag_stat, user_tier, tag_skills_dict)
        score += level_up_bonus

        # 3. 타겟 정렬 가중치 (Requirement 4: 타겟 태그와 일치하면 +30점)
        target_score = 30 if (target_tag_ids and tag_stat.tag_id.value in target_tag_ids) else 0
        score += target_score

        return score

    def _calculate_level_up_bonus(
        self,
        tag_stat: TagAccountStat,
        user_tier: TierId,
        tag_skills_dict: dict[tuple[int, SkillCode], TagSkill]
    ) -> float:
        """승급 임박 보너스 점수 계산"""
        # 현재 숙련도 찾기
        current_skill = self._match_tag_skill(tag_stat, user_tier, tag_skills_dict)
        if not current_skill:
            return 0.0

        # 같은 태그 내에서 다음 숙련도 결정 (IM→AD, AD→MAS)
        next_skill_code = self._SKILL_CODE_ORDER.get(current_skill.skill_code)
        if not next_skill_code:
            # 마지막 숙련도(MASTER)이면 보너스 없음
            return 0.0

        next_skill = tag_skills_dict.get((tag_stat.tag_id.value, next_skill_code))
        if not next_skill:
            return 0.0

        # 다음 레벨까지 필요한 문제 수
        current_solved = tag_stat.solved_problem_count
        required_solved = next_skill.requirements.min_solved_problem
        problems_needed = required_solved - current_solved

        # 5문제 미만 남았으면 30점 부여
        if 0 < problems_needed < 5:
            return 30.0

        return 0.0