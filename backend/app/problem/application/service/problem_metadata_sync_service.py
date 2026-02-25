"""
ProblemMetadataSyncService - 주간 문제/태그 메타데이터 동기화 서비스

solved.ac API에서 전체 태그·문제 데이터를 가져와 DB를 upsert하고,
태그별 난이도 범위 및 tag_skill을 재계산한다.

기존에는 외부 subprocess(solvedac_tag_collector.py, solvedac_problem_collector.py,
db_initializer.py)로 처리하던 것을, 앱 내부 서비스로 이관하여
앱의 DB 세션 컨텍스트를 공유한다.
"""
from __future__ import annotations

import asyncio
import json
import logging
from dataclasses import dataclass
from datetime import datetime

import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.common.domain.entity.system_log import SystemLog
from app.common.domain.repository.system_log_repository import SystemLogRepository
from app.config.tag_config import TAG_CONFIG
from app.core.database import Database, transactional

logger = logging.getLogger(__name__)

_BATCH_SIZE = 500       # 문제 upsert 배치 크기
_PAGE_DELAY = 0.5       # 페이지 요청 간 딜레이 (초)


@dataclass
class SyncResult:
    """sync_all() 결과"""
    tag_count: int
    problem_count: int


class ProblemMetadataSyncService:
    """
    solved.ac 전체 태그·문제 데이터를 DB와 동기화한다.

    스케줄러(BjAccountUpdateScheduler)가 set_database_context()로
    DB 컨텍스트를 설정한 뒤 sync_all()을 호출한다.
    """

    SOLVED_AC_TAG_LIST_URL = "https://solved.ac/api/v3/tag/list"
    SOLVED_AC_PROBLEM_SEARCH_URL = "https://solved.ac/api/v3/search/problem"

    def __init__(self, db: Database, system_log_repository: SystemLogRepository | None = None) -> None:
        self.db = db
        self.system_log_repository = system_log_repository

    @property
    def session(self) -> AsyncSession:
        return self.db.get_current_session()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def sync_all(self) -> SyncResult:
        """전체 동기화 수행. 결과(처리된 태그·문제 수)를 반환."""
        logger.info("[ProblemMetadataSyncService] sync_all: starting weekly sync")

        tag_count = await self.sync_tags()
        logger.info(f"[ProblemMetadataSyncService] sync_all: tags done ({tag_count})")

        problem_count = await self.sync_problems()
        logger.info(f"[ProblemMetadataSyncService] sync_all: problems done ({problem_count})")

        await self.recalculate_tag_tier_ranges()
        logger.info("[ProblemMetadataSyncService] sync_all: tag tier ranges recalculated")

        await self.recalculate_tag_skills()
        logger.info("[ProblemMetadataSyncService] sync_all: tag skills recalculated")

        logger.info("[ProblemMetadataSyncService] sync_all: completed successfully")
        return SyncResult(tag_count=tag_count, problem_count=problem_count)

    # ------------------------------------------------------------------
    # 1. 태그 동기화
    # ------------------------------------------------------------------

    @transactional
    async def sync_tags(self) -> int:
        """
        solved.ac /api/v3/tag/list 에서 전체 태그를 가져와
        tag 테이블에 upsert한다.

        TAG_CONFIG에 있는 태그 → excluded_yn=False, 해당 level 적용
        TAG_CONFIG에 없는 태그 → excluded_yn=True, level="NEWBIE"

        Returns:
            처리된 태그 수
        """
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(self.SOLVED_AC_TAG_LIST_URL)
            response.raise_for_status()
            tags_data: list[dict] = response.json().get("items", [])

        now = datetime.now()

        for item in tags_data:
            tag_code: str = item["key"]
            config = TAG_CONFIG.get(tag_code)

            if config is not None:
                level = config["level"]
                excluded = False
            else:
                level = "NEWBIE"
                excluded = True

            ko_name = next(
                (n["name"] for n in item.get("displayNames", []) if n["language"] == "ko"),
                tag_code,
            )

            await self.session.execute(
                text("""
                    INSERT INTO tag (
                        tag_code, tag_level, excluded_yn,
                        tag_display_name, tag_problem_count,
                        aliases, min_solved_person_count,
                        created_at, updated_at
                    )
                    VALUES (
                        :code, :lvl, :ex,
                        :display, :cnt,
                        :ali, 1000,
                        :now, :now
                    )
                    ON DUPLICATE KEY UPDATE
                        tag_problem_count   = VALUES(tag_problem_count),
                        tag_display_name    = VALUES(tag_display_name),
                        excluded_yn         = VALUES(excluded_yn),
                        updated_at          = VALUES(updated_at)
                """),
                {
                    "code": tag_code,
                    "lvl": level,
                    "ex": excluded,
                    "display": ko_name,
                    "cnt": item.get("problemCount", 0),
                    "ali": json.dumps(item.get("aliases", [])),
                    "now": now,
                },
            )

        logger.info(f"[ProblemMetadataSyncService] sync_tags: upserted {len(tags_data)} tags")
        return len(tags_data)

    # ------------------------------------------------------------------
    # 2. 문제 동기화
    # ------------------------------------------------------------------

    async def sync_problems(self) -> int:
        """
        solved.ac /api/v3/search/problem?query=&page=N 에서 전체 문제를
        페이지네이션으로 수집한 뒤 problem + problem_tag 테이블에 upsert한다.

        - 페이지당 0.5초 딜레이 (rate limit 대응)
        - _BATCH_SIZE(500)개 단위로 트랜잭션을 분리해 커밋한다
        - problem_tag는 INSERT IGNORE (FK 안전)

        Returns:
            처리된 문제 수
        """
        # 태그 코드 → tag_id 매핑 미리 로드
        async with self.db.session() as session:
            result = await session.execute(text("SELECT tag_id, tag_code FROM tag"))
            tag_code_to_id: dict[str, int] = {row[1]: row[0] for row in result.fetchall()}

        # 첫 페이지로 전체 개수 파악
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.get(
                self.SOLVED_AC_PROBLEM_SEARCH_URL,
                params={"query": "", "page": 1},
            )
            resp.raise_for_status()
            first_page = resp.json()

        total: int = first_page.get("count", 0)
        first_items: list[dict] = first_page.get("items", [])
        per_page = len(first_items) if first_items else 50
        total_pages = (total + per_page - 1) // per_page if per_page > 0 else 1

        all_problems: list[dict] = list(first_items)
        logger.info(
            f"[ProblemMetadataSyncService] sync_problems: total={total}, pages={total_pages}"
        )

        # 나머지 페이지 순차 수집
        for page in range(2, total_pages + 1):
            await asyncio.sleep(_PAGE_DELAY)
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    page_resp = await client.get(
                        self.SOLVED_AC_PROBLEM_SEARCH_URL,
                        params={"query": "", "page": page},
                    )
                    if page_resp.status_code != 200:
                        logger.warning(
                            f"[ProblemMetadataSyncService] page {page} returned "
                            f"{page_resp.status_code}, skipping"
                        )
                        continue
                    all_problems.extend(page_resp.json().get("items", []))
            except Exception as exc:
                logger.error(f"[ProblemMetadataSyncService] page {page} failed: {exc}")
                continue

            if page % 100 == 0:
                logger.info(
                    f"[ProblemMetadataSyncService] sync_problems: "
                    f"fetched {page}/{total_pages} pages"
                )

        logger.info(
            f"[ProblemMetadataSyncService] sync_problems: "
            f"fetched {len(all_problems)} problems, starting DB upsert"
        )

        # _BATCH_SIZE 단위로 배치 upsert
        now = datetime.now()
        processed = 0

        for i in range(0, len(all_problems), _BATCH_SIZE):
            batch = all_problems[i : i + _BATCH_SIZE]
            async with self.db.session() as session:
                for prob in batch:
                    problem_id = prob["problemId"]

                    await session.execute(
                        text("""
                            INSERT INTO problem (
                                problem_id, problem_title,
                                problem_tier_level, solved_user_count,
                                created_at, updated_at
                            )
                            VALUES (
                                :id, :title,
                                :lvl, :solved_count,
                                :now, :now
                            )
                            ON DUPLICATE KEY UPDATE
                                problem_tier_level  = VALUES(problem_tier_level),
                                solved_user_count   = VALUES(solved_user_count),
                                updated_at          = VALUES(updated_at)
                        """),
                        {
                            "id": problem_id,
                            "title": prob.get("titleKo", ""),
                            "lvl": prob.get("level", 0),
                            "solved_count": prob.get("acceptedUserCount", 0),
                            "now": now,
                        },
                    )

                    for tag_obj in prob.get("tags", []):
                        tag_id = tag_code_to_id.get(tag_obj.get("key", ""))
                        if tag_id:
                            await session.execute(
                                text("""
                                    INSERT IGNORE INTO problem_tag (problem_id, tag_id, created_at)
                                    VALUES (:pid, :tid, :now)
                                """),
                                {"pid": problem_id, "tid": tag_id, "now": now},
                            )

            processed += len(batch)
            logger.info(
                f"[ProblemMetadataSyncService] sync_problems: "
                f"upserted {processed}/{len(all_problems)} problems"
            )

        return len(all_problems)

    # ------------------------------------------------------------------
    # 3. 태그 티어 범위 재계산
    # ------------------------------------------------------------------

    @transactional
    async def recalculate_tag_tier_ranges(self) -> None:
        """
        각 태그별 문제 티어 분포(하위 10% · 상위 20% 절사)를 기반으로
        tag 테이블의 min_problem_tier_id / max_problem_tier_id를 업데이트한다.

        db_initializer._update_tag_tier_range()와 동일한 로직.
        """
        logger.info("[ProblemMetadataSyncService] recalculate_tag_tier_ranges: starting")

        tag_result = await self.session.execute(text("SELECT tag_id FROM tag"))
        tag_ids: list[int] = [row[0] for row in tag_result.fetchall()]

        now = datetime.now()

        for tag_id in tag_ids:
            tiers_result = await self.session.execute(
                text("""
                    SELECT p.problem_tier_level
                    FROM problem p
                    JOIN problem_tag pt ON p.problem_id = pt.problem_id
                    WHERE pt.tag_id = :tag_id
                    ORDER BY p.problem_tier_level ASC
                """),
                {"tag_id": tag_id},
            )
            tier_list = [row[0] for row in tiers_result.fetchall()]

            if not tier_list:
                continue

            total_count = len(tier_list)
            lower_trim_idx = int(total_count * 0.1)   # 하위 10% 제거
            upper_trim_idx = int(total_count * 0.8)   # 상위 20% 제거

            if upper_trim_idx <= lower_trim_idx:
                lower_trim_idx = 0
                upper_trim_idx = total_count

            trimmed = tier_list[lower_trim_idx:upper_trim_idx]
            trimmed_count = len(trimmed)

            # 절사 목록에서 상위 90% 지점 → min_tier
            min_tier_idx = min(int(trimmed_count * 0.9), trimmed_count - 1)
            min_tier_id = trimmed[min_tier_idx]
            max_tier_id = trimmed[-1]

            await self.session.execute(
                text("""
                    UPDATE tag
                    SET min_problem_tier_id = :min_tier,
                        max_problem_tier_id = :max_tier,
                        updated_at          = :now
                    WHERE tag_id = :tag_id
                """),
                {
                    "min_tier": min_tier_id,
                    "max_tier": max_tier_id,
                    "tag_id": tag_id,
                    "now": now,
                },
            )

        logger.info("[ProblemMetadataSyncService] recalculate_tag_tier_ranges: done")

    # ------------------------------------------------------------------
    # 4. tag_skill 재계산
    # ------------------------------------------------------------------

    @transactional
    async def recalculate_tag_skills(self) -> None:
        """
        태그별 문제 티어 백분위를 기반으로 tag_skill(IM/AD/MAS) 레코드를
        INSERT ON DUPLICATE KEY UPDATE로 갱신한다.

        db_initializer._setup_tag_skills()와 동일한 로직.
        주의: problem_recommendation_level_filter는 건드리지 않는다 (정적 데이터).
        """
        logger.info("[ProblemMetadataSyncService] recalculate_tag_skills: starting")

        tag_result = await self.session.execute(
            text("SELECT tag_id, tag_level, tag_code FROM tag")
        )
        tags = tag_result.fetchall()

        now = datetime.now()

        for tag_id_val, tag_level, tag_code in tags:
            # solved_user_count >= 1000 인 문제의 티어 분포
            tiers_result = await self.session.execute(
                text("""
                    SELECT p.problem_tier_level
                    FROM problem p
                    JOIN problem_tag pt ON p.problem_id = pt.problem_id
                    WHERE pt.tag_id = :tag_id AND p.solved_user_count >= 1000
                    ORDER BY p.problem_tier_level ASC
                """),
                {"tag_id": tag_id_val},
            )
            tier_list = [row[0] for row in tiers_result.fetchall()]

            if not tier_list:
                logger.debug(
                    f"[ProblemMetadataSyncService] recalculate_tag_skills: "
                    f"no problems for tag {tag_code} (id={tag_id_val}), using default tier=1"
                )
                tier_list = [1]

            trimmed_count = len(tier_list)

            def get_percentile_tier(percentile: float) -> int:
                """백분위수(0.0~1.0)에 해당하는 티어 반환"""
                target = 1.0 - percentile
                idx = min(trimmed_count - 1, int(trimmed_count * target))
                return tier_list[idx]

            master_user_tier     = get_percentile_tier(0.5)
            master_highest_tier  = get_percentile_tier(0.1)
            advanced_user_tier   = get_percentile_tier(0.7)
            advanced_highest_tier = get_percentile_tier(0.4)
            immediate_user_tier  = tier_list[0]
            immediate_highest_tier = tier_list[0]

            # 태그 레벨별 권장 문제 수
            if tag_level in ("NEWBIE", "BEGINNER"):
                m_cnt, a_cnt = 15, 10
            elif tag_level == "REQUIREMENT":
                m_cnt, a_cnt = 10, 7
            else:
                m_cnt, a_cnt = 7, 5

            im_period, ad_period, mas_period = 3, 7, 14

            for sc, mp, mut, mspt, period in [
                ("IM",  0,     immediate_user_tier,  immediate_highest_tier,  im_period),
                ("AD",  a_cnt, advanced_user_tier,   advanced_highest_tier,   ad_period),
                ("MAS", m_cnt, master_user_tier,     master_highest_tier,     mas_period),
            ]:
                await self.session.execute(
                    text("""
                        INSERT INTO tag_skill (
                            tag_id, tag_level, tag_skill_code,
                            min_solved_problem, min_user_tier, min_solved_problem_tier,
                            recommendation_period, created_at, updated_at, active_yn
                        )
                        VALUES (
                            :tag_id, :lvl, :sc,
                            :mp, :mut, :mspt,
                            :period, :now, :now, :yn
                        )
                        ON DUPLICATE KEY UPDATE
                            min_solved_problem      = VALUES(min_solved_problem),
                            min_user_tier           = VALUES(min_user_tier),
                            min_solved_problem_tier = VALUES(min_solved_problem_tier),
                            recommendation_period   = VALUES(recommendation_period),
                            updated_at              = VALUES(updated_at)
                    """),
                    {
                        "tag_id": tag_id_val,
                        "lvl": tag_level,
                        "sc": sc,
                        "mp": mp,
                        "mut": mut,
                        "mspt": mspt,
                        "period": period,
                        "now": now,
                        "yn": True,
                    },
                )

        logger.info("[ProblemMetadataSyncService] recalculate_tag_skills: done")

    # ------------------------------------------------------------------
    # 5. system_log 저장 (트랜잭션 보장)
    # ------------------------------------------------------------------

    @transactional
    async def save_sync_result_log(self, log: SystemLog) -> None:
        """
        주간 동기화 결과 system_log를 저장한다.

        스케줄러 finally 블록에서 호출되며, @transactional이 새 세션을
        열어주므로 sync_all() 완료 후에도 안전하게 저장할 수 있다.
        """
        if self.system_log_repository is None:
            logger.warning("[ProblemMetadataSyncService] system_log_repository not injected, skipping log save")
            return
        await self.system_log_repository.save(log)
