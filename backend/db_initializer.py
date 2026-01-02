import json
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datetime import datetime
import logging

# 프로젝트 루트를 sys.path에 추가
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

load_dotenv()

# Config를 활용하여 환경별 DB URL 가져오기
from app.config.settings import settings

def get_db_url():
    """환경에 따라 적절한 DB URL 반환"""
    mysql_host = getattr(settings, 'MYSQL_HOST', 'localhost')
    mysql_port = getattr(settings, 'MYSQL_PORT', 3306)
    mysql_user = settings.MYSQL_USERNAME
    mysql_password = settings.MYSQL_PASSWORD
    mysql_db = settings.MYSQL_DATABASE

    return f"mysql+mysqldb://{mysql_user}:{mysql_password}@{mysql_host}:{mysql_port}/{mysql_db}"

DB_URL = get_db_url()
engine = create_engine(DB_URL)

# 2. 비즈니스 규칙 상수 정의
TIERS = [
    {"tier_id": 0, "tier_level": 0, "tier_code": "Unrated", "tier_rating": 0},
    # Bronze 5 ~ 1
    {"tier_id": 1, "tier_level": 1, "tier_code": "B5", "tier_rating": 30},
    {"tier_id": 2, "tier_level": 2, "tier_code": "B4", "tier_rating": 60},
    {"tier_id": 3, "tier_level": 3, "tier_code": "B3", "tier_rating": 90},
    {"tier_id": 4, "tier_level": 4, "tier_code": "B2", "tier_rating": 120},
    {"tier_id": 5, "tier_level": 5, "tier_code": "B1", "tier_rating": 150},
    # Silver 5 ~ 1
    {"tier_id": 6, "tier_level": 6, "tier_code": "S5", "tier_rating": 200},
    {"tier_id": 7, "tier_level": 7, "tier_code": "S4", "tier_rating": 300},
    {"tier_id": 8, "tier_level": 8, "tier_code": "S3", "tier_rating": 400},
    {"tier_id": 9, "tier_level": 9, "tier_code": "S2", "tier_rating": 500},
    {"tier_id": 10, "tier_level": 10, "tier_code": "S1", "tier_rating": 650},
    # Gold 5 ~ 1
    {"tier_id": 11, "tier_level": 11, "tier_code": "G5", "tier_rating": 800},
    {"tier_id": 12, "tier_level": 12, "tier_code": "G4", "tier_rating": 950},
    {"tier_id": 13, "tier_level": 13, "tier_code": "G3", "tier_rating": 1100},
    {"tier_id": 14, "tier_level": 14, "tier_code": "G2", "tier_rating": 1250},
    {"tier_id": 15, "tier_level": 15, "tier_code": "G1", "tier_rating": 1400},
    # Platinum 5 ~ 1
    {"tier_id": 16, "tier_level": 16, "tier_code": "P5", "tier_rating": 1600},
    {"tier_id": 17, "tier_level": 17, "tier_code": "P4", "tier_rating": 1750},
    {"tier_id": 18, "tier_level": 18, "tier_code": "P3", "tier_rating": 1900},
    {"tier_id": 19, "tier_level": 19, "tier_code": "P2", "tier_rating": 2000},
    {"tier_id": 20, "tier_level": 20, "tier_code": "P1", "tier_rating": 2100},
    # Diamond 5 ~ 1
    {"tier_id": 21, "tier_level": 21, "tier_code": "D5", "tier_rating": 2200},
    {"tier_id": 22, "tier_level": 22, "tier_code": "D4", "tier_rating": 2300},
    {"tier_id": 23, "tier_level": 23, "tier_code": "D3", "tier_rating": 2400},
    {"tier_id": 24, "tier_level": 24, "tier_code": "D2", "tier_rating": 2500},
    {"tier_id": 25, "tier_level": 25, "tier_code": "D1", "tier_rating": 2600},
    # Ruby 5 ~ 1 (C1은 Ruby 5 수준 혹은 그 이상으로 매칭)
    {"tier_id": 26, "tier_level": 26, "tier_code": "R5", "tier_rating": 2700},
    {"tier_id": 27, "tier_level": 27, "tier_code": "R4", "tier_rating": 2750},
    {"tier_id": 28, "tier_level": 28, "tier_code": "R3", "tier_rating": 2800},
    {"tier_id": 29, "tier_level": 29, "tier_code": "R2", "tier_rating": 2900},
    {"tier_id": 30, "tier_level": 30, "tier_code": "R1", "tier_rating": 2950},
    # Master
    {"tier_id": 31, "tier_level": 31, "tier_code": "M1", "tier_rating": 3000},
]

LEVELS = ["NEWBIE", "BEGINNER", "REQUIREMENT", "DETAIL", "CHALLENGE"]

TAG_CONFIG = {
    # 쌩기초 (BEGINNER)
    "수학": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "정렬": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "기하학": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "사칙연산": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "정수론": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "조합론": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "소수 판정": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    
    # 기초알고리즘 (BEGINNER)
    "구현": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "그리디 알고리즘": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "문자열": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "브루트포스 알고리즘": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "트리": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "집합과 맵": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "시뮬레이션": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": ["구현"]},
    "누적 합": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "너비 우선 탐색": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "깊이 우선 탐색": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "해시를 사용한 집합과 맵": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": ["집합과 맵"]},
    "백트래킹": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "스택": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "재귀": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "임의 정밀도 / 큰 수 연산": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "에라토스테네스의 체": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "덱": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "큐": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},

    # 필수알고리즘 (REQUIREMENT)
    "다이나믹 프로그래밍": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "애드 혹": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "이분 탐색": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["집합과 맵"]},
    "최단 경로": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["깊이 우선 탐색", "너비 우선 탐색"]},
    "비트마스킹": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "분리 집합": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "트리를 사용한 집합과 맵": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["집합과 맵", "트리"]},
    "우선순위 큐": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["스택", "큐"]},
    "분할 정복": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "투 포인터": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "유클리드 호제법": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "격자 그래프": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "슬라이딩 윈도우": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["투 포인터"]},

    # 세부알고리즘 (DETAIL)
    "세그먼트 트리": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["트리", "스택"]},
    "데이크스트라": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["최단 경로"]},
    "최대 유량": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": []},
    "트라이": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["문자열"]},
    "최소 스패닝 트리": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["우선순위 큐"]},
    "위상 정렬": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["트리"]},
    "최소 공통 조상": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["트리"]},
    "플로이드–워셜": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["최단 경로"]},
    "느리게 갱신되는 세그먼트 트리": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["세그먼트 트리"]},
    "트리에서의 다이나믹 프로그래밍": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["다이나믹 프로그래밍", "트리"]},
    "비트필드를 이용한 다이나믹 프로그래밍": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["다이나믹 프로그래밍", "비트마스킹"]},
    "배낭 문제": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["다이나믹 프로그래밍"]},
    "역추적": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["다이나믹 프로그래밍"]},
    "가장 긴 증가하는 부분 수열: o(n log n)": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["다이나믹 프로그래밍"]},

    # 도전알고리즘 (CHALLENGE)
    "최소 비용 최대 유량": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["최대 유량"]},
    "KMP": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["문자열"]},
    "외판원 순회": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["비트필드를 이용한 다이나믹 프로그래밍"]},
    "이분 매칭": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["최대 유량"]},
    "강한 연결 요소": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["깊이 우선 탐색", "스택"]},
    "볼록 껍질": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["기하학"]}
}

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("migration_debug.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class DBMigrator:
    def __init__(self, engine):
        self.engine = engine
        self.tag_id_map = {}
        self.target_id_map = {}
        self.skill_id_map = {}
        self.missing_tags = set() # 설정에 누락된 태그 수집용  
    
    def load_json(self, path):
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def execute_init(self):
        try:
            tags_data = self.load_json('data/tags.json')['items']
            problems_data = self.load_json('data/problems.json')['items']

            with self.engine.begin() as conn:
                conn.execute(text("SET SESSION sql_mode = CONCAT(@@sql_mode, ',NO_AUTO_VALUE_ON_ZERO');"))

                now = datetime.now()
                logger.info(f"Migration started at {now}")

                self._setup_tiers(conn, now)
                self._setup_targets(conn, now)
                self._migrate_tags(conn, tags_data, now)
                self._migrate_problems(conn, problems_data, now)

                # 문제 삽입 후 태그의 min/max_problem_tier_id 업데이트
                self._update_tag_tier_range(conn, now)

                self._setup_tag_relations(conn, now)

                # 문제 데이터를 기반으로 tag_skill의 티어 계산
                self._setup_tag_skills(conn, now)

                self._setup_filters(conn, now)

                # 누락된 태그 리포트
                if self.missing_tags:
                    logger.warning(f"Total {len(self.missing_tags)} tags were missing in TAG_CONFIG: {self.missing_tags}")

                logger.info("Migration successful!")
        except Exception as e:
            logger.error(f"Critical error during migration: {str(e)}")
            # engine.begin()에 의해 자동으로 Rollback 됩니다.
            raise e

    def _setup_tiers(self, conn, now):
        for tier in TIERS:
            conn.execute(text("""
                INSERT INTO tier (tier_id, tier_level, tier_code, tier_rating, created_at, updated_at)
                VALUES (:tid, :tlvl, :tcode, :trat, :now, :now)
                ON DUPLICATE KEY UPDATE 
                    tier_level = VALUES(tier_level),
                    tier_code = VALUES(tier_code),
                    tier_rating = VALUES(tier_rating),
                    updated_at = VALUES(updated_at)
            """), {
                "tid": tier["tier_id"], "tlvl": tier["tier_level"], 
                "tcode": tier["tier_code"], "trat": tier["tier_rating"], "now": now
            })

    def _setup_targets(self, conn, now):
        for code in ["DAILY", "CT", "BEGINNER"]:
            conn.execute(text("""
                INSERT INTO target (target_code, active_yn, target_display_name, created_at, updated_at) 
                VALUES (:c, :active, :c, :now, :now)
                ON DUPLICATE KEY UPDATE updated_at = VALUES(updated_at)
            """), {"c": code, "active": True, "now": now})
            
            res = conn.execute(text("SELECT target_id FROM target WHERE target_code = :c"), {"c": code}).fetchone()
            self.target_id_map[code] = res[0]

    def _migrate_tags(self, conn, tags_data, now):
        for item in tags_data:
            ko_name = next((n['name'] for n in item['displayNames'] if n['language'] == 'ko'), item['key'])
            config = TAG_CONFIG.get(ko_name, {"level": "NEWBIE", "goals": [], "excluded": True})

            conn.execute(text("""
                INSERT INTO tag (tag_code, tag_level, excluded_yn, min_solved_person_count, aliases, tag_problem_count, tag_display_name, created_at, updated_at)
                VALUES (:code, :lvl, :ex, :min_s, :ali, :cnt, :display_name, :now, :now)
                ON DUPLICATE KEY UPDATE
                    tag_problem_count = VALUES(tag_problem_count),
                    tag_display_name = VALUES(tag_display_name),
                    updated_at = VALUES(updated_at)
            """), {
                "code": item['key'], "lvl": config['level'], "ex": config.get("excluded", False),
                "min_s": 1000, "ali": json.dumps(item['aliases']), "cnt": item['problemCount'],
                "display_name": ko_name, "now": now
            })
            
            tag_id = conn.execute(text("SELECT tag_id FROM tag WHERE tag_code = :c"), {"c": item['key']}).fetchone()[0]
            self.tag_id_map[ko_name] = tag_id
            self.tag_id_map[item['key']] = tag_id

            for g_code in config['goals']:
                conn.execute(text("""
                    INSERT IGNORE INTO target_tag (tag_id, target_id, created_at, updated_at) 
                    VALUES (:tid, :target_id, :now, :now)
                """), {"tid": tag_id, "target_id": self.target_id_map[g_code], "now": now})

    def _migrate_problems(self, conn, problems_data, now):
        for prob in problems_data:
            conn.execute(text("""
                INSERT INTO problem (problem_id, problem_title, problem_tier_level, created_at, updated_at)
                VALUES (:id, :title, :lvl, :now, :now)
                ON DUPLICATE KEY UPDATE 
                    problem_tier_level = VALUES(problem_tier_level),
                    updated_at = VALUES(updated_at)
            """), {"id": prob['problemId'], "title": prob['titleKo'], "lvl": prob['level'], "now": now})

            for t_obj in prob.get('tags', []):
                t_id = self.tag_id_map.get(t_obj['key'])
                if t_id:
                    conn.execute(text("""
                        INSERT IGNORE INTO problem_tag (problem_id, tag_id, created_at) 
                        VALUES (:pid, :tid, :now)
                    """), {"pid": prob['problemId'], "tid": t_id, "now": now})

    def _setup_tag_relations(self, conn, now):
        for sub_name, config in TAG_CONFIG.items():
            sub_id = self.tag_id_map.get(sub_name)
            for p_name in config.get('parents', []):
                p_id = self.tag_id_map.get(p_name)
                if sub_id and p_id:
                    conn.execute(text("""
                        INSERT IGNORE INTO tag_relation (leading_tag_id, sub_tag_id, created_at, updated_at)
                        VALUES (:p, :s, :now, :now)
                    """), {"p": p_id, "s": sub_id, "now": now})

    def _update_tag_tier_range(self, conn, now):
        """각 태그별 문제 티어 범위(상위/하위 10%)를 계산하여 업데이트"""
        logger.info("Calculating tag tier ranges...")

        # 모든 태그에 대해 처리
        for tag_id in self.tag_id_map.values():
            # 해당 태그의 모든 문제 티어를 가져옴 (티어 오름차순)
            tiers = conn.execute(text("""
                SELECT p.problem_tier_level
                FROM problem p
                JOIN problem_tag pt ON p.problem_id = pt.problem_id
                WHERE pt.tag_id = :tag_id
                ORDER BY p.problem_tier_level ASC
            """), {"tag_id": tag_id}).fetchall()

            if not tiers:
                continue

            tier_list = [t[0] for t in tiers]
            total_count = len(tier_list)

            # 하위 10% 인덱스 (0-based)
            lower_10_idx = max(0, int(total_count * 0.1) - 1)
            # 상위 10% 인덱스 (0-based)
            upper_10_idx = min(total_count - 1, int(total_count * 0.9))

            min_tier_id = tier_list[lower_10_idx]
            max_tier_id = tier_list[upper_10_idx]

            # 태그 업데이트
            conn.execute(text("""
                UPDATE tag
                SET min_problem_tier_id = :min_tier,
                    max_problem_tier_id = :max_tier,
                    updated_at = :now
                WHERE tag_id = :tag_id
            """), {"min_tier": min_tier_id, "max_tier": max_tier_id, "tag_id": tag_id, "now": now})

        logger.info("Tag tier ranges updated successfully")

    def _setup_tag_skills(self, conn, now):
        """레벨별 문제 티어 분포를 기반으로 tag_skill 테이블 설정"""
        logger.info("Setting up tag skills with tier calculations...")

        skill_id_map = {}

        for lvl in LEVELS:
            # 해당 레벨에 속한 모든 문제의 티어를 가져옴
            tiers = conn.execute(text("""
                SELECT DISTINCT p.problem_tier_level
                FROM problem p
                JOIN problem_tag pt ON p.problem_id = pt.problem_id
                JOIN tag t ON pt.tag_id = t.tag_id
                WHERE t.tag_level = :lvl
                ORDER BY p.problem_tier_level ASC
            """), {"lvl": lvl}).fetchall()

            if not tiers:
                logger.warning(f"No problems found for level {lvl}, using default tier 1")
                tier_list = [1]
            else:
                tier_list = [t[0] for t in tiers]

            total_count = len(tier_list)

            # 백분위수 계산
            def get_percentile_tier(percentile):
                """백분위수에 해당하는 티어 반환 (percentile: 0.0 ~ 1.0)"""
                idx = min(total_count - 1, int(total_count * percentile))
                return tier_list[idx]

            # Master: user-tier 50%, highest 10%
            master_user_tier = get_percentile_tier(0.5)
            master_highest_tier = get_percentile_tier(0.1)

            # Advanced: user-tier 70%, highest 40%
            advanced_user_tier = get_percentile_tier(0.7)
            advanced_highest_tier = get_percentile_tier(0.4)

            # Immediate: 기본값 (tier_id=1)
            immediate_user_tier = tier_list[0] if tier_list else 1
            immediate_highest_tier = tier_list[0] if tier_list else 1

            # 문제 수 설정
            if lvl in ["NEWBIE", "BEGINNER"]:
                m_cnt, a_cnt = 15, 10
            elif lvl == "REQUIREMENT":
                m_cnt, a_cnt = 10, 7
            else:
                m_cnt, a_cnt = 7, 5

            # Immediate 삽입
            conn.execute(text("""
                INSERT INTO tag_skill (tag_level, tag_skill_code, min_solved_problem, min_user_tier, min_solved_problem_tier, created_at, updated_at, active_yn)
                VALUES (:lvl, :sc, :mp, :mut, :mspt, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    min_solved_problem = VALUES(min_solved_problem),
                    min_user_tier = VALUES(min_user_tier),
                    min_solved_problem_tier = VALUES(min_solved_problem_tier),
                    updated_at = VALUES(updated_at)
            """), {"lvl": lvl, "sc": "IM", "mp": 0, "mut": immediate_user_tier, "mspt": immediate_highest_tier, "now": now, "yn": True})

            sid = conn.execute(text("SELECT tag_skill_id FROM tag_skill WHERE tag_level=:lvl AND tag_skill_code=:sc"),
                               {"lvl": lvl, "sc": "IM"}).fetchone()[0]
            skill_id_map[(lvl, "IM")] = sid

            # Advanced 삽입
            conn.execute(text("""
                INSERT INTO tag_skill (tag_level, tag_skill_code, min_solved_problem, min_user_tier, min_solved_problem_tier, created_at, updated_at, active_yn)
                VALUES (:lvl, :sc, :mp, :mut, :mspt, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    min_solved_problem = VALUES(min_solved_problem),
                    min_user_tier = VALUES(min_user_tier),
                    min_solved_problem_tier = VALUES(min_solved_problem_tier),
                    updated_at = VALUES(updated_at)
            """), {"lvl": lvl, "sc": "AD", "mp": a_cnt, "mut": advanced_user_tier, "mspt": advanced_highest_tier, "now": now, "yn": True})

            sid = conn.execute(text("SELECT tag_skill_id FROM tag_skill WHERE tag_level=:lvl AND tag_skill_code=:sc"),
                               {"lvl": lvl, "sc": "AD"}).fetchone()[0]
            skill_id_map[(lvl, "AD")] = sid

            # Master 삽입
            conn.execute(text("""
                INSERT INTO tag_skill (tag_level, tag_skill_code, min_solved_problem, min_user_tier, min_solved_problem_tier, created_at, updated_at, active_yn)
                VALUES (:lvl, :sc, :mp, :mut, :mspt, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    min_solved_problem = VALUES(min_solved_problem),
                    min_user_tier = VALUES(min_user_tier),
                    min_solved_problem_tier = VALUES(min_solved_problem_tier),
                    updated_at = VALUES(updated_at)
            """), {"lvl": lvl, "sc": "MAS", "mp": m_cnt, "mut": master_user_tier, "mspt": master_highest_tier, "now": now, "yn": True})

            sid = conn.execute(text("SELECT tag_skill_id FROM tag_skill WHERE tag_level=:lvl AND tag_skill_code=:sc"),
                               {"lvl": lvl, "sc": "MAS"}).fetchone()[0]
            skill_id_map[(lvl, "MAS")] = sid

        self.skill_id_map = skill_id_map
        logger.info("Tag skills setup completed with calculated tiers")

    def _setup_filters(self, conn, now):
        """문제 추천 난이도 필터 설정"""
        logger.info("Setting up recommendation level filters...")

        filter_data = [
            ("EASY", "쉬움", -5, None, "IM", 100),
            ("NORMAL", "보통", 0, -1, "AD", 20),
            ("HARD", "어려움", 2, 1, "AD", 40),
            ("EXTREME", "매우 어려움", 10, 2, "MAS", 10)
        ]
        for f_code, d_name, min_d, max_d, s_code, rate in filter_data:
            s_id = self.skill_id_map.get(("BEGINNER", s_code))
            conn.execute(text("""
                INSERT INTO problem_recommendation_level_filter (filter_code, display_name, min_user_tier_diff, max_user_tier_diff, tag_skill_id, tag_skill_rate, created_at, updated_at, active_yn)
                VALUES (:fc, :dn, :min, :max, :sid, :rate, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    display_name = VALUES(display_name),
                    updated_at = VALUES(updated_at)
            """), {"fc": f_code, "dn": d_name, "min": min_d, "max": max_d, "sid": s_id, "rate": rate, "now": now, "yn": True})

        logger.info("Recommendation level filters setup completed")
    
    def truncate_all_tables(self):
        tables = [
            "problem_recommendation_level_filter", "tag_skill", "tag_relation", 
            "problem_tag", "target_tag", "problem", "tag", "target", "tier"
        ]
        with self.engine.begin() as conn:
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 0;"))
            for table in tables:
                conn.execute(text(f"TRUNCATE TABLE {table};"))
            conn.execute(text("SET FOREIGN_KEY_CHECKS = 1;"))
            logger.info("All tables truncated successfully.")
            
if __name__ == "__main__":
    migrator = DBMigrator(engine)
    migrator.execute_init()