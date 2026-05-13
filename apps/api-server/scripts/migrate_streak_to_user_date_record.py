"""
streak → user_date_record / problem_date_record 데이터 마이그레이션 스크립트

실행 순서:
  1. alembic upgrade b1c2d3e4f5a6
  2. python scripts/migrate_streak_to_user_date_record.py [--dry-run]
  3. alembic upgrade c2d3e4f5a6b7

사용법:
  python scripts/migrate_streak_to_user_date_record.py           # 실제 실행
  python scripts/migrate_streak_to_user_date_record.py --dry-run # 건수만 확인
"""

import argparse
import logging
import sys
from pathlib import Path

# db_initializer.py와 동일한 방식으로 프로젝트 루트를 경로에 추가
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from dotenv import load_dotenv
load_dotenv()

from app.config.settings import settings
from sqlalchemy import create_engine, text

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)


def get_engine():
    mysql_host = getattr(settings, 'MYSQL_HOST', 'localhost')
    mysql_port = getattr(settings, 'MYSQL_PORT', 3306)
    db_url = (
        f"mysql+mysqldb://{settings.MYSQL_USERNAME}:{settings.MYSQL_PASSWORD}"
        f"@{mysql_host}:{mysql_port}/{settings.MYSQL_DATABASE}"
    )
    return create_engine(db_url)


def run_migration(dry_run: bool = False) -> None:
    engine = get_engine()

    with engine.begin() as conn:
        # streak 테이블 존재 확인
        streak_exists = conn.execute(text(
            "SELECT COUNT(*) FROM information_schema.tables "
            "WHERE table_schema = DATABASE() AND table_name = 'streak'"
        )).scalar()

        if not streak_exists:
            logger.error("streak 테이블이 없습니다. alembic upgrade b1c2d3e4f5a6 를 먼저 실행하세요.")
            return

        # =====================================================================
        # Step 0.5: problem_history → user_problem_status 누락분 채우기
        #
        # 리팩토링(c69f522) 이전 연동된 계정은 link 시점에 user_problem_status가
        # 생성되지 않았음 (구버전은 problem_history만 저장).
        # → Step 2의 JOIN이 성공하려면 user_problem_status 행이 먼저 있어야 함.
        #
        # account_link를 거쳐 (user_account_id, bj_account_id, problem_id)를 확정:
        #   - 활성 account_link(deleted_at IS NULL) 우선
        #   - 이미 ups 행이 있으면 INSERT IGNORE로 skip
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 0.5: problem_history → user_problem_status 누락분 채우기")
        logger.info("  [구버전 연동 계정의 user_problem_status 복원]")
        logger.info("=" * 60)

        ups_missing_cnt = conn.execute(text("""
            SELECT COUNT(*)
            FROM problem_history ph
            JOIN account_link al
                ON al.bj_account_id = ph.bj_account_id
            WHERE NOT EXISTS (
                SELECT 1
                FROM user_problem_status ups
                WHERE ups.user_account_id = al.user_account_id
                  AND ups.problem_id      = ph.problem_id
            )
        """)).scalar()
        logger.info(f"  user_problem_status 누락 대상: {ups_missing_cnt}건")

        if not dry_run and ups_missing_cnt > 0:
            result = conn.execute(text("""
                INSERT IGNORE INTO user_problem_status
                    (user_account_id, bj_account_id, problem_id,
                     banned_yn, solved_yn, created_at, updated_at)
                SELECT
                    al.user_account_id,
                    ph.bj_account_id,
                    ph.problem_id,
                    FALSE,
                    TRUE,
                    NOW(),
                    NOW()
                FROM problem_history ph
                JOIN account_link al
                    ON al.bj_account_id = ph.bj_account_id
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM user_problem_status ups
                    WHERE ups.user_account_id = al.user_account_id
                      AND ups.problem_id      = ph.problem_id
                )
            """))
            logger.info(f"  → {result.rowcount}건 삽입 완료")

        # =====================================================================
        # Step 0: user_problem_status.bj_account_id backfill
        #
        # alembic upgrade b1c2d3e4f5a6 이후 기존 행은 bj_account_id = NULL 상태.
        # READ 쿼리가 bj_account_id = 활성계정으로 필터링하므로, NULL이면 아무것도 안 보임.
        #
        # 처리 방식:
        #   - BANNED(banned_yn=TRUE): 유저 레벨 → bj_account_id = NULL 유지
        #   - SOLVED/WILL_SOLVE: 해당 유저의 최신 account_link(활성 우선)로 설정
        #
        # 유의: 계정을 변경한 유저의 경우 이전 계정 시절 데이터가 새 계정으로
        #       배정되지만, 현재 DB에서 연결 시점을 알 수 없어 최선의 방법.
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 0: user_problem_status.bj_account_id backfill")
        logger.info("  [기존 행에 bj_account_id 역채움 — BANNED 제외]")
        logger.info("=" * 60)

        ups_null_cnt = conn.execute(text("""
            SELECT COUNT(*)
            FROM user_problem_status
            WHERE bj_account_id IS NULL
              AND banned_yn = FALSE
        """)).scalar()
        logger.info(f"  bj_account_id 미설정(SOLVED/WILL_SOLVE) 대상: {ups_null_cnt}건")

        # ------------------------------------------------------------------
        # Step 0 사전 정리: 이전 부분 실행으로 target bj_account_id 행이 이미
        # 존재하는 NULL 행은 UPDATE 시 중복 key 에러가 발생하므로 먼저 삭제한다.
        # ------------------------------------------------------------------
        dup_null_cnt = conn.execute(text("""
            SELECT COUNT(ups_null.user_problem_status_id)
            FROM user_problem_status ups_null
            JOIN (
                SELECT user_account_id, bj_account_id
                FROM (
                    SELECT user_account_id, bj_account_id,
                           ROW_NUMBER() OVER (
                               PARTITION BY user_account_id
                               ORDER BY
                                   CASE WHEN deleted_at IS NULL THEN 0 ELSE 1 END,
                                   created_at DESC
                           ) AS rn
                    FROM account_link
                ) al_sub WHERE al_sub.rn = 1
            ) latest_al ON latest_al.user_account_id = ups_null.user_account_id
            JOIN user_problem_status ups_real
                ON ups_real.user_account_id = ups_null.user_account_id
                AND ups_real.bj_account_id  = latest_al.bj_account_id
                AND ups_real.problem_id     = ups_null.problem_id
            WHERE ups_null.bj_account_id IS NULL
              AND ups_null.banned_yn = FALSE
        """)).scalar()
        logger.info(f"  중복 NULL 행 (target bj_account_id 이미 존재): {dup_null_cnt}건")

        if not dry_run and dup_null_cnt > 0:
            # 1) problem_date_record FK를 새 ups_real로 재연결
            #    (NULL로 끊지 않고 바로 교체 → pdr 데이터 보존)
            conn.execute(text("""
                UPDATE problem_date_record pdr
                JOIN user_problem_status ups_null
                    ON pdr.user_problem_status_id = ups_null.user_problem_status_id
                JOIN (
                    SELECT user_account_id, bj_account_id
                    FROM (
                        SELECT user_account_id, bj_account_id,
                               ROW_NUMBER() OVER (
                                   PARTITION BY user_account_id
                                   ORDER BY
                                       CASE WHEN deleted_at IS NULL THEN 0 ELSE 1 END,
                                       created_at DESC
                               ) AS rn
                        FROM account_link
                    ) al_sub WHERE al_sub.rn = 1
                ) latest_al ON latest_al.user_account_id = ups_null.user_account_id
                JOIN user_problem_status ups_real
                    ON ups_real.user_account_id = ups_null.user_account_id
                    AND ups_real.bj_account_id  = latest_al.bj_account_id
                    AND ups_real.problem_id     = ups_null.problem_id
                SET pdr.user_problem_status_id = ups_real.user_problem_status_id
                WHERE ups_null.bj_account_id IS NULL
                  AND ups_null.banned_yn = FALSE
            """))
            # 2) 중복 NULL 행 삭제
            del_result = conn.execute(text("""
                DELETE ups_null FROM user_problem_status ups_null
                JOIN (
                    SELECT user_account_id, bj_account_id
                    FROM (
                        SELECT user_account_id, bj_account_id,
                               ROW_NUMBER() OVER (
                                   PARTITION BY user_account_id
                                   ORDER BY
                                       CASE WHEN deleted_at IS NULL THEN 0 ELSE 1 END,
                                       created_at DESC
                               ) AS rn
                        FROM account_link
                    ) al_sub WHERE al_sub.rn = 1
                ) latest_al ON latest_al.user_account_id = ups_null.user_account_id
                JOIN user_problem_status ups_real
                    ON ups_real.user_account_id = ups_null.user_account_id
                    AND ups_real.bj_account_id  = latest_al.bj_account_id
                    AND ups_real.problem_id     = ups_null.problem_id
                WHERE ups_null.bj_account_id IS NULL
                  AND ups_null.banned_yn = FALSE
            """))
            logger.info(f"  → {del_result.rowcount}건 삭제 완료")

        # 유저별 최신 account_link: 활성(deleted_at IS NULL) 우선, 그 다음 created_at 내림차순
        if not dry_run and ups_null_cnt > 0:
            result = conn.execute(text("""
                UPDATE user_problem_status ups
                JOIN (
                    SELECT
                        user_account_id,
                        bj_account_id,
                        ROW_NUMBER() OVER (
                            PARTITION BY user_account_id
                            ORDER BY
                                CASE WHEN deleted_at IS NULL THEN 0 ELSE 1 END,
                                created_at DESC
                        ) AS rn
                    FROM account_link
                ) latest_al
                    ON latest_al.user_account_id = ups.user_account_id
                    AND latest_al.rn = 1
                SET ups.bj_account_id = latest_al.bj_account_id
                WHERE ups.bj_account_id IS NULL
                  AND ups.banned_yn = FALSE
            """))
            logger.info(f"  → {result.rowcount}건 backfill 완료")

        ups_still_null = conn.execute(text("""
            SELECT COUNT(*)
            FROM user_problem_status
            WHERE bj_account_id IS NULL
              AND banned_yn = FALSE
        """)).scalar()
        if ups_still_null:
            logger.warning(f"  ⚠️  backfill 후에도 bj_account_id=NULL인 SOLVED/WILL_SOLVE: {ups_still_null}건 (account_link 없는 유저)")

        # =====================================================================
        # Step 1: problem_date_record.user_account_id backfill
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 1: problem_date_record.user_account_id backfill")
        logger.info("=" * 60)

        target_cnt = conn.execute(text("""
            SELECT COUNT(*)
            FROM problem_date_record pdr
            JOIN user_problem_status ups
                ON pdr.user_problem_status_id = ups.user_problem_status_id
            WHERE pdr.user_account_id IS NULL
              AND pdr.user_problem_status_id IS NOT NULL
        """)).scalar()
        logger.info(f"  backfill 대상: {target_cnt}건")

        if not dry_run and target_cnt > 0:
            result = conn.execute(text("""
                UPDATE problem_date_record pdr
                JOIN user_problem_status ups
                    ON pdr.user_problem_status_id = ups.user_problem_status_id
                SET pdr.user_account_id = ups.user_account_id
                WHERE pdr.user_account_id IS NULL
                  AND pdr.user_problem_status_id IS NOT NULL
            """))
            logger.info(f"  → {result.rowcount}건 backfill 완료")

        # =====================================================================
        # Step 2: problem_history × streak → problem_date_record (SOLVED)
        #
        # 스케줄러가 발견한 날짜(streak_date)를 문제별 SOLVED 기록으로 이전
        # JOIN: problem_history → streak → account_link(전체) → user_problem_status
        #
        # Step 0에서 user_problem_status.bj_account_id가 채워졌으므로,
        # bj_account_id 일치 조건으로 정확히 매칭.
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 2: problem_history × streak → problem_date_record (SOLVED)")
        logger.info("  [스케줄러 발견 날짜 → 문제별 날짜 기록 생성]")
        logger.info("=" * 60)

        pdr_target_cnt = conn.execute(text("""
            SELECT COUNT(*)
            FROM problem_history ph
            JOIN streak s
                ON ph.streak_id = s.streak_id
            JOIN account_link al
                ON al.bj_account_id = ph.bj_account_id
            JOIN user_problem_status ups
                ON ups.user_account_id = al.user_account_id
                AND ups.problem_id = ph.problem_id
                AND ups.bj_account_id = al.bj_account_id
                AND ups.banned_yn = FALSE
            WHERE ph.streak_id IS NOT NULL
              AND NOT EXISTS (
                  SELECT 1
                  FROM problem_date_record pdr
                  WHERE pdr.user_problem_status_id = ups.user_problem_status_id
                    AND pdr.record_type = 'SOLVED'
                    AND pdr.deleted_at IS NULL
              )
        """)).scalar()
        logger.info(f"  신규 problem_date_record(SOLVED) 생성 대상: {pdr_target_cnt}건")

        null_streak_cnt = conn.execute(text(
            "SELECT COUNT(*) FROM problem_history WHERE streak_id IS NULL"
        )).scalar()
        logger.info(f"  streak_id IS NULL인 problem_history (날짜 미매핑, skip): {null_streak_cnt}건")

        if not dry_run and pdr_target_cnt > 0:
            result = conn.execute(text("""
                INSERT INTO problem_date_record (
                    user_problem_status_id,
                    user_account_id,
                    marked_date,
                    record_type,
                    display_order,
                    created_at,
                    updated_at
                )
                SELECT
                    ups.user_problem_status_id,
                    ups.user_account_id,
                    s.streak_date,
                    'SOLVED',
                    0,
                    NOW(),
                    NOW()
                FROM problem_history ph
                JOIN streak s
                    ON ph.streak_id = s.streak_id
                JOIN account_link al
                    ON al.bj_account_id = ph.bj_account_id
                JOIN user_problem_status ups
                    ON ups.user_account_id = al.user_account_id
                    AND ups.problem_id = ph.problem_id
                    AND ups.bj_account_id = al.bj_account_id
                    AND ups.banned_yn = FALSE
                WHERE ph.streak_id IS NOT NULL
                  AND NOT EXISTS (
                      SELECT 1
                      FROM problem_date_record pdr
                      WHERE pdr.user_problem_status_id = ups.user_problem_status_id
                        AND pdr.record_type = 'SOLVED'
                        AND pdr.deleted_at IS NULL
                  )
            """))
            logger.info(f"  → {result.rowcount}건 삽입 완료")

        # =====================================================================
        # Step 3: SOLVED 중복 soft delete
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 3: SOLVED 중복 정리 (동일 user_problem_status + 날짜)")
        logger.info("=" * 60)

        dup_rows = conn.execute(text("""
            SELECT user_problem_status_id, marked_date, COUNT(*) as cnt
            FROM problem_date_record
            WHERE record_type = 'SOLVED'
              AND deleted_at IS NULL
              AND user_problem_status_id IS NOT NULL
            GROUP BY user_problem_status_id, marked_date
            HAVING cnt > 1
        """)).fetchall()

        logger.info(f"  중복 그룹: {len(dup_rows)}건")
        if not dry_run:
            deleted_total = 0
            for row in dup_rows:
                ups_id, marked_date, cnt = row
                result = conn.execute(text("""
                    UPDATE problem_date_record
                    SET deleted_at = NOW()
                    WHERE user_problem_status_id = :ups_id
                      AND marked_date = :marked_date
                      AND record_type = 'SOLVED'
                      AND deleted_at IS NULL
                      AND problem_date_record_id != (
                          SELECT min_id FROM (
                              SELECT MIN(problem_date_record_id) AS min_id
                              FROM problem_date_record
                              WHERE user_problem_status_id = :ups_id
                                AND marked_date = :marked_date
                                AND record_type = 'SOLVED'
                                AND deleted_at IS NULL
                          ) sub
                      )
                """), {"ups_id": ups_id, "marked_date": marked_date})
                deleted_total += result.rowcount
            logger.info(f"  → {deleted_total}건 soft delete 완료")

        # =====================================================================
        # Step 3.5: cross-date SOLVED 중복 정리 (Req 2, Req 3)
        #
        # 동일 user_problem_status_id에 서로 다른 날짜의 활성 SOLVED가 여러 개인 경우
        # → 가장 이른(빠른) 날짜 1건 유지, 나머지 soft delete
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 3.5: cross-date SOLVED 중복 정리 (이른 날짜 유지)")
        logger.info("=" * 60)

        dup_ups_rows = conn.execute(text("""
            SELECT user_problem_status_id, COUNT(*) AS cnt
            FROM problem_date_record
            WHERE record_type = 'SOLVED'
              AND deleted_at IS NULL
              AND user_problem_status_id IS NOT NULL
            GROUP BY user_problem_status_id
            HAVING cnt > 1
        """)).fetchall()

        logger.info(f"  cross-date SOLVED 중복 ups 수: {len(dup_ups_rows)}건")

        if not dry_run:
            deleted_total = 0
            for row in dup_ups_rows:
                ups_id, cnt = row
                result = conn.execute(text("""
                    UPDATE problem_date_record
                    SET deleted_at = NOW()
                    WHERE user_problem_status_id = :ups_id
                      AND record_type = 'SOLVED'
                      AND deleted_at IS NULL
                      AND problem_date_record_id != (
                          SELECT keep_id FROM (
                              SELECT problem_date_record_id AS keep_id
                              FROM problem_date_record
                              WHERE user_problem_status_id = :ups_id
                                AND record_type = 'SOLVED'
                                AND deleted_at IS NULL
                              ORDER BY marked_date ASC, problem_date_record_id ASC
                              LIMIT 1
                          ) sub
                      )
                """), {"ups_id": ups_id})
                deleted_total += result.rowcount
            logger.info(f"  → {deleted_total}건 soft delete 완료 (이른 날짜 유지)")

        # =====================================================================
        # Step 4: streak × account_link(전체) → user_date_record (일별 delta)
        #
        # streak.solved_count는 전역 누적값이므로 SUM이 아닌 delta 계산 필요:
        #   일별 풀이수 = MAX(당일 solved_count) - MAX(전날까지 solved_count, 없으면 0)
        #   → MySQL 8.0 LAG 윈도우 함수로 처리
        #
        # account_link 필터: deleted_at 무관 (과거 연동 포함)
        #   → bj_account_id가 UNIQUE KEY에 포함되므로 계정별로 분리 저장
        #
        # 주의: solvedac 가입 이전 데이터는 단건에 큰 누적값이 기록될 수 있으나
        #       첫 행의 delta = MAX(당일) - 0 이므로 정상 처리됨
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 4: streak × account_link(전체) → user_date_record (일별 delta)")
        logger.info("  [streak.solved_count 전역 누적값 → 일별 delta 변환, 과거 연동 포함]")
        logger.info("=" * 60)

        udr_target = conn.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT al.user_account_id, al.bj_account_id, dd.streak_date
                FROM (
                    SELECT
                        bj_account_id,
                        streak_date,
                        MAX(solved_count) - COALESCE(
                            LAG(MAX(solved_count)) OVER (
                                PARTITION BY bj_account_id ORDER BY streak_date
                            ), 0
                        ) AS daily_count
                    FROM streak
                    GROUP BY bj_account_id, streak_date
                ) dd
                JOIN (SELECT DISTINCT user_account_id, bj_account_id FROM account_link) al
                    ON al.bj_account_id = dd.bj_account_id
                WHERE dd.daily_count > 0
                  AND NOT EXISTS (
                      SELECT 1 FROM user_date_record udr
                      WHERE udr.user_account_id = al.user_account_id
                        AND udr.bj_account_id = al.bj_account_id
                        AND udr.marked_date = dd.streak_date
                  )
            ) t
        """)).scalar()
        logger.info(f"  user_date_record 생성 대상: {udr_target}건")

        if not dry_run and udr_target > 0:
            result = conn.execute(text("""
                INSERT INTO user_date_record
                    (user_account_id, bj_account_id, marked_date, solved_count, created_at, updated_at)
                SELECT
                    al.user_account_id,
                    al.bj_account_id,
                    dd.streak_date,
                    dd.daily_count,
                    NOW(),
                    NOW()
                FROM (
                    SELECT
                        bj_account_id,
                        streak_date,
                        MAX(solved_count) - COALESCE(
                            LAG(MAX(solved_count)) OVER (
                                PARTITION BY bj_account_id ORDER BY streak_date
                            ), 0
                        ) AS daily_count
                    FROM streak
                    GROUP BY bj_account_id, streak_date
                ) dd
                JOIN (SELECT DISTINCT user_account_id, bj_account_id FROM account_link) al
                    ON al.bj_account_id = dd.bj_account_id
                WHERE dd.daily_count > 0
                  AND NOT EXISTS (
                      SELECT 1 FROM user_date_record udr
                      WHERE udr.user_account_id = al.user_account_id
                        AND udr.bj_account_id = al.bj_account_id
                        AND udr.marked_date = dd.streak_date
                  )
            """))
            logger.info(f"  → {result.rowcount}건 삽입 완료")

        # =====================================================================
        # Step 4.5: problem_date_record(SOLVED) 기반 user_date_record 갱신/생성
        #
        # 수동으로 매핑된 날짜가 streak과 다를 수 있으므로, 실제 활성 SOLVED 개수로
        # user_date_record를 덮어씁니다 (ON DUPLICATE KEY UPDATE).
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 4.5: problem_date_record(SOLVED) 기반 user_date_record 갱신")
        logger.info("  [활성 SOLVED 매핑 날짜의 solved_count를 실제 개수로 동기화]")
        logger.info("=" * 60)

        udr_update_target = conn.execute(text("""
            SELECT COUNT(*) FROM (
                SELECT pdr.user_account_id, ups.bj_account_id, pdr.marked_date, COUNT(*) AS cnt
                FROM problem_date_record pdr
                JOIN user_problem_status ups
                    ON pdr.user_problem_status_id = ups.user_problem_status_id
                WHERE pdr.record_type = 'SOLVED'
                  AND pdr.deleted_at IS NULL
                  AND pdr.user_account_id IS NOT NULL
                  AND ups.bj_account_id IS NOT NULL
                GROUP BY pdr.user_account_id, ups.bj_account_id, pdr.marked_date
            ) t
        """)).scalar()
        logger.info(f"  user_date_record UPSERT 대상: {udr_update_target}건")

        if not dry_run and udr_update_target > 0:
            result = conn.execute(text("""
                INSERT INTO user_date_record
                    (user_account_id, bj_account_id, marked_date, solved_count, created_at, updated_at)
                SELECT
                    pdr.user_account_id,
                    ups.bj_account_id,
                    pdr.marked_date,
                    COUNT(*) AS solved_count,
                    NOW(),
                    NOW()
                FROM problem_date_record pdr
                JOIN user_problem_status ups
                    ON pdr.user_problem_status_id = ups.user_problem_status_id
                WHERE pdr.record_type = 'SOLVED'
                  AND pdr.deleted_at IS NULL
                  AND pdr.user_account_id IS NOT NULL
                  AND ups.bj_account_id IS NOT NULL
                GROUP BY pdr.user_account_id, ups.bj_account_id, pdr.marked_date
                ON DUPLICATE KEY UPDATE
                    solved_count = VALUES(solved_count),
                    updated_at = NOW()
            """))
            logger.info(f"  → {result.rowcount}건 UPSERT 완료")

        # =====================================================================
        # Step 5: 검증
        # =====================================================================
        logger.info("=" * 60)
        logger.info("Step 5: 검증")
        logger.info("=" * 60)

        udr_total  = conn.execute(text("SELECT COUNT(*) FROM user_date_record")).scalar()
        pdr_solved = conn.execute(text(
            "SELECT COUNT(*) FROM problem_date_record WHERE record_type='SOLVED' AND deleted_at IS NULL"
        )).scalar()
        pdr_null_ua = conn.execute(text(
            "SELECT COUNT(*) FROM problem_date_record "
            "WHERE user_account_id IS NULL AND user_problem_status_id IS NOT NULL"
        )).scalar()
        ph_with_streak = conn.execute(text(
            "SELECT COUNT(*) FROM problem_history WHERE streak_id IS NOT NULL"
        )).scalar()
        ups_total = conn.execute(text("SELECT COUNT(*) FROM user_problem_status")).scalar()
        ups_null_bj = conn.execute(text(
            "SELECT COUNT(*) FROM user_problem_status "
            "WHERE bj_account_id IS NULL AND banned_yn = FALSE"
        )).scalar()

        logger.info(f"  user_date_record 총 건수:                    {udr_total}")
        logger.info(f"  problem_date_record(SOLVED, 활성) 총:         {pdr_solved}")
        logger.info(f"  problem_history(streak_id 있음):              {ph_with_streak}")
        logger.info(f"  user_problem_status 총 건수:                  {ups_total}")
        if pdr_null_ua:
            logger.warning(f"  ⚠️  pdr user_account_id 누락: {pdr_null_ua}건")
        if ups_null_bj:
            logger.warning(f"  ⚠️  ups bj_account_id 누락(SOLVED/WILL_SOLVE): {ups_null_bj}건 (account_link 없는 유저)")

        if dry_run:
            # engine.begin()은 with 블록 종료 시 자동 commit하므로 rollback을 위해 예외를 던짐
            raise _DryRunRollback()

    logger.info("")
    logger.info("✅ 마이그레이션 완료")
    logger.info("다음 단계: alembic upgrade c2d3e4f5a6b7  (streak 테이블 DROP)")


class _DryRunRollback(Exception):
    """dry-run 시 트랜잭션 롤백용 내부 예외"""


def main():
    parser = argparse.ArgumentParser(description="streak → user_date_record / problem_date_record 마이그레이션")
    parser.add_argument("--dry-run", action="store_true", help="실제 변경 없이 대상 건수만 확인")
    args = parser.parse_args()

    logger.info(f"=== streak 마이그레이션 {'[DRY-RUN]' if args.dry_run else '[실행]'} ===")

    try:
        run_migration(dry_run=args.dry_run)
    except _DryRunRollback:
        logger.info("")
        logger.info("✅ [DRY-RUN] 완료 — 실제 변경 없음 (트랜잭션 롤백)")
    except Exception as e:
        logger.error(f"❌ 마이그레이션 실패: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
