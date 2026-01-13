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
    "math": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "sorting": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "geometry": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "arithmetic": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "number_theory": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "combinatorics": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    "primality_test": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER"], "parents": []},
    
    # 기초알고리즘 (BEGINNER)
    "implementation": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "greedy": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "string": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "bruteforcing": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "trees": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "set": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "simulation": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": ["implementation"]},
    "prefix_sum": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "bfs": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "dfs": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "hash_set": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": ["set"]},
    "backtracking": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "stack": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "recursion": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "arbitrary_precision": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "sieve": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "deque": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},
    "queue": {"level": "BEGINNER", "goals": ["DAILY", "BEGINNER", "CT"], "parents": []},

    # 필수알고리즘 (REQUIREMENT)
    "dp": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "ad_hoc": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "binary_search": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["set"]},
    "shortest_path": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["dfs", "bfs"]},
    "bitmask": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "disjoint_set": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "tree_set": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["set", "trees"]},
    "priority_queue": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["stack", "queue"]},
    "divide_and_conquer": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "two_pointer": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "euclidean": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "grid_graph": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": []},
    "sliding_window": {"level": "REQUIREMENT", "goals": ["DAILY", "CT"], "parents": ["two_pointer"]},

    # 세부알고리즘 (DETAIL)
    "segtree": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["trees", "stack"]},
    "dijkstra": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["shortest_path"]},
    "flow": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": []},
    "trie": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["string"]},
    "mst": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["priority_queue"]},
    "topological_sorting": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["trees"]},
    "lca": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["trees"]},
    "floyd_warshall": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["shortest_path"]},
    "lazyprop": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["segtree"]},
    "dp_tree": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp", "trees"]},
    "dp_bitfield": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp", "bitmask"]},
    "knapsack": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp"]},
    "traceback": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp"]},
    "lis": {"level": "DETAIL", "goals": ["DAILY", "CT"], "parents": ["dp"]},

    # 도전알고리즘 (CHALLENGE)
    "mcmf": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["flow"]},
    "kmp": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["string"]},
    "tsp": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["dp_bitfield"]},
    "bipartite_matching": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["flow"]},
    "scc": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["dfs", "stack"]},
    "convex_hull": {"level": "CHALLENGE", "goals": ["DAILY"], "parents": ["geometry"]}
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

    def _validate_tag_config(self, tags_data):
        """TAG_CONFIG와 tags.json 간 일관성 검증"""
        logger.info("Validating TAG_CONFIG consistency...")

        issues = []

        # tags.json의 모든 태그 코드와 한글명 추출
        tag_mapping = {}
        for item in tags_data:
            ko_name = next((n['name'] for n in item['displayNames'] if n['language'] == 'ko'), item['key'])
            tag_mapping[item['key']] = ko_name

        # TAG_CONFIG 검증
        for tag_name, config in TAG_CONFIG.items():
            # 1. 태그가 tags.json에 존재하는지
            if tag_name not in tag_mapping.values() and tag_name not in tag_mapping.keys():
                issues.append(f"TAG_CONFIG에는 있지만 tags.json에 없음: {tag_name}")

            # 2. 부모 태그들이 모두 TAG_CONFIG에 존재하는지
            for parent in config.get('parents', []):
                if parent not in TAG_CONFIG:
                    issues.append(f"존재하지 않는 부모 태그 참조: {tag_name} -> {parent}")

        # tags.json에는 있지만 TAG_CONFIG에 없는 태그들
        for tag_code, ko_name in tag_mapping.items():
            if ko_name not in TAG_CONFIG and tag_code not in TAG_CONFIG:
                issues.append(f"tags.json에는 있지만 TAG_CONFIG에 없음: {ko_name} ({tag_code})")

        if issues:
            logger.warning(f"Found {len(issues)} TAG_CONFIG issues:")
            for issue in issues:
                logger.warning(f"  - {issue}")
        else:
            logger.info("TAG_CONFIG validation passed!")

        return issues

    def _normalize_tag_config(self, tags_data):
        """Convert Korean parent names to English keys in TAG_CONFIG"""
        logger.info("Normalizing TAG_CONFIG parent references...")

        # Build Korean -> English key mapping from tags.json
        ko_to_key = {}
        key_to_ko = {}
        for item in tags_data:
            key = item['key']
            ko_name = next((n['name'] for n in item['displayNames'] if n['language'] == 'ko'), key)
            ko_to_key[ko_name] = key
            key_to_ko[key] = ko_name

        # Normalize TAG_CONFIG in place
        normalized_config = {}
        for tag_key, config in TAG_CONFIG.items():
            # Convert tag_key if it's Korean (most are already English)
            eng_key = ko_to_key.get(tag_key, tag_key)

            # Convert parent names to English keys
            normalized_parents = []
            for parent in config.get('parents', []):
                parent_key = ko_to_key.get(parent, parent)
                normalized_parents.append(parent_key)

            # Create normalized config entry
            normalized_config[eng_key] = {
                **config,
                'parents': normalized_parents
            }

        logger.info(f"TAG_CONFIG normalized: {len(normalized_config)} tags processed")
        return normalized_config, ko_to_key, key_to_ko

    def execute_init(self):
        try:
            tags_data = self.load_json('data/tags.json')['items']
            problems_data = self.load_json('data/problems.json')['items']

            # Normalize TAG_CONFIG before processing (convert Korean parent names to English keys)
            global TAG_CONFIG
            TAG_CONFIG, self.ko_to_key, self.key_to_ko = self._normalize_tag_config(tags_data)

            # Validate TAG_CONFIG after normalization
            validation_issues = self._validate_tag_config(tags_data)
            if validation_issues:
                logger.warning("Proceeding with migration despite validation issues")

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

            # Try key first (English), fallback to Korean name for backwards compatibility
            config = TAG_CONFIG.get(item['key'])
            if not config:
                config = {"level": "NEWBIE", "goals": [], "excluded": True}
                self.missing_tags.add(item['key'])

            # Determine excluded_reason if tag is excluded
            excluded_reason = None
            if config.get("excluded", False):
                excluded_reason = self._determine_excluded_reason(item, config)

            conn.execute(text("""
                INSERT INTO tag (tag_code, tag_level, excluded_yn, excluded_reason, min_solved_person_count, aliases, tag_problem_count, tag_display_name, created_at, updated_at)
                VALUES (:code, :lvl, :ex, :ex_reason, :min_s, :ali, :cnt, :display_name, :now, :now)
                ON DUPLICATE KEY UPDATE
                    tag_problem_count = VALUES(tag_problem_count),
                    tag_display_name = VALUES(tag_display_name),
                    excluded_yn = VALUES(excluded_yn),
                    excluded_reason = VALUES(excluded_reason),
                    updated_at = VALUES(updated_at)
            """), {
                "code": item['key'],
                "lvl": config['level'],
                "ex": config.get("excluded", False),
                "ex_reason": excluded_reason,
                "min_s": 1000,
                "ali": json.dumps(item['aliases']),
                "cnt": item['problemCount'],
                "display_name": ko_name,
                "now": now
            })
            
            tag_id = conn.execute(text("SELECT tag_id FROM tag WHERE tag_code = :c"), {"c": item['key']}).fetchone()[0]
            self.tag_id_map[ko_name] = tag_id
            self.tag_id_map[item['key']] = tag_id

            for g_code in config['goals']:
                conn.execute(text("""
                    INSERT IGNORE INTO target_tag (tag_id, target_id, created_at, updated_at) 
                    VALUES (:tid, :target_id, :now, :now)
                """), {"tid": tag_id, "target_id": self.target_id_map[g_code], "now": now})

    def _determine_excluded_reason(self, tag_item, config):
        """Determine excluded reason based on TODO.md rules"""
        problem_count = tag_item['problemCount']
        tag_key = tag_item['key']

        # Rule 1: Minor tags (difficult + few problems with 1000+ solvers)
        # Approximation: very low problem count (지협적인 태그)
        if problem_count < 50:
            return "MINOR"

        # Rule 2: Comprehensive tags (has many sub-tags) (포괄적 태그)
        comprehensive_tags = {
            "data_structures", "graphs", "graph_traversal", "ds",
            "number_theory", "geometry"
        }
        if tag_key in comprehensive_tags:
            return "COMPREHENSIVE"

        # Rule 3: Insignificant tags (not important algorithmically) (중요하지 않은 태그)
        insignificant_tags = {
            "game_theory", "offline_queries", "coordinate_compression",
            "constructive", "parsing", "regex", "case_work"
        }
        if tag_key in insignificant_tags:
            return "INSIGNIFICANT"

        # Default to INSIGNIFICANT for unknown excluded tags
        return "INSIGNIFICANT"

    def _migrate_problems(self, conn, problems_data, now):
        for prob in problems_data:
            conn.execute(text("""
                INSERT INTO problem (problem_id, problem_title, problem_tier_level, solved_user_count, created_at, updated_at)
                VALUES (:id, :title, :lvl, :solved_count, :now, :now)
                ON DUPLICATE KEY UPDATE
                    problem_tier_level = VALUES(problem_tier_level),
                    solved_user_count = VALUES(solved_user_count),
                    updated_at = VALUES(updated_at)
            """), {
                "id": prob['problemId'],
                "title": prob['titleKo'],
                "lvl": prob['level'],
                "solved_count": prob.get('acceptedUserCount', 0),
                "now": now
            })

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
        """각 태그별 문제 티어 범위 계산 (상위 20%, 하위 10% 절사 후)"""
        logger.info("Calculating tag tier ranges with trimming...")

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

            # 상위 20%, 하위 10% 절사
            lower_trim_idx = int(total_count * 0.1)  # 하위 10% 제거
            upper_trim_idx = int(total_count * 0.8)  # 상위 20% 제거 (0.8 = 1.0 - 0.2)

            # 인덱스 보정 (최소 1개 이상의 문제는 남겨야 함)
            if upper_trim_idx <= lower_trim_idx:
                lower_trim_idx = 0
                upper_trim_idx = total_count

            trimmed_list = tier_list[lower_trim_idx:upper_trim_idx]
            trimmed_count = len(trimmed_list)

            # 절사된 목록에서 최소티어 (상위 90%)
            min_tier_idx = int(trimmed_count * 0.9)
            min_tier_idx = min(min_tier_idx, trimmed_count - 1)  # 경계 체크
            min_tier_id = trimmed_list[min_tier_idx]

            # 최대티어는 절사된 목록의 최대값
            max_tier_id = trimmed_list[-1]

            # 태그 업데이트
            conn.execute(text("""
                UPDATE tag
                SET min_problem_tier_id = :min_tier,
                    max_problem_tier_id = :max_tier,
                    updated_at = :now
                WHERE tag_id = :tag_id
            """), {"min_tier": min_tier_id, "max_tier": max_tier_id, "tag_id": tag_id, "now": now})

            logger.debug(f"Tag {tag_id}: total={total_count}, trimmed={trimmed_count}, "
                        f"min_tier={min_tier_id}, max_tier={max_tier_id}")

        logger.info("Tag tier ranges updated successfully with trimming")

    def _setup_tag_skills(self, conn, now):
        """태그별 문제 티어 분포를 기반으로 tag_skill 테이블 설정 (절사 적용)"""
        logger.info("Setting up per-tag tag skills with trimmed tier calculations...")

        # 기존 global tag_skill 레코드 삭제 (tag_id가 NULL인 것들)
        # 주의: problem_recommendation_level_filter가 tag_skill_id를 참조하므로 먼저 삭제
        logger.info("Deleting dependent records first...")

        # Step 1: problem_recommendation_level_filter의 기존 레코드 삭제
        filter_result = conn.execute(text("DELETE FROM problem_recommendation_level_filter"))
        logger.info(f"Deleted {filter_result.rowcount} old level_filter records")

        # Step 2: 이제 tag_skill의 기존 global 레코드 삭제 가능
        skill_result = conn.execute(text("DELETE FROM tag_skill WHERE tag_id IS NULL"))
        logger.info(f"Deleted {skill_result.rowcount} old global tag_skill records (tag_id=NULL)")

        skill_id_map = {}

        # Iterate through ALL tags (not just levels)
        for tag_id in self.tag_id_map.values():
            # Get tag info
            tag_info = conn.execute(text("""
                SELECT tag_id, tag_level, tag_code FROM tag WHERE tag_id = :tid
            """), {"tid": tag_id}).fetchone()

            if not tag_info:
                continue

            tag_id_val, tag_level, tag_code = tag_info

            # Get tier distribution for THIS SPECIFIC TAG
            tiers = conn.execute(text("""
                SELECT p.problem_tier_level
                FROM problem p
                JOIN problem_tag pt ON p.problem_id = pt.problem_id
                WHERE pt.tag_id = :tag_id
                ORDER BY p.problem_tier_level ASC
            """), {"tag_id": tag_id_val}).fetchall()

            if not tiers:
                logger.warning(f"No problems found for tag {tag_code} (id={tag_id_val}), using default tier 1")
                tier_list = [1]
            else:
                tier_list = [t[0] for t in tiers]

            total_count = len(tier_list)

            # 상위 20%, 하위 10% 절사
            lower_trim_idx = int(total_count * 0.1)
            upper_trim_idx = int(total_count * 0.8)

            if upper_trim_idx <= lower_trim_idx:
                trimmed_list = tier_list
            else:
                trimmed_list = tier_list[lower_trim_idx:upper_trim_idx]

            trimmed_count = len(trimmed_list)

            # 백분위수 계산 함수 (절사된 목록 기준)
            def get_percentile_tier(percentile):
                """백분위수에 해당하는 티어 반환 (percentile: 0.0 ~ 1.0)"""
                target_percentile = 1.0 - percentile 
                idx = min(trimmed_count - 1, int(trimmed_count * target_percentile))
                return trimmed_list[idx]

            # Master: user-tier 50%, highest 10%
            master_user_tier = get_percentile_tier(0.5)
            master_highest_tier = get_percentile_tier(0.1)

            # Advanced: user-tier 70%, highest 40%
            advanced_user_tier = get_percentile_tier(0.7)
            advanced_highest_tier = get_percentile_tier(0.4)

            # Intermediate: 최소 티어
            immediate_user_tier = trimmed_list[0] if trimmed_list else 1
            immediate_highest_tier = trimmed_list[0] if trimmed_list else 1

            # 문제 수 설정 (태그 레벨에 따라)
            if tag_level in ["NEWBIE", "BEGINNER"]:
                m_cnt, a_cnt = 15, 10
            elif tag_level == "REQUIREMENT":
                m_cnt, a_cnt = 10, 7
            else:
                m_cnt, a_cnt = 7, 5

            # Recommendation period 설정
            im_period, ad_period, mas_period = 3, 7, 14

            # Immediate 삽입
            conn.execute(text("""
                INSERT INTO tag_skill (tag_id, tag_level, tag_skill_code,
                                     min_solved_problem, min_user_tier, min_solved_problem_tier,
                                     recommendation_period, created_at, updated_at, active_yn)
                VALUES (:tag_id, :lvl, :sc, :mp, :mut, :mspt, :period, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    min_solved_problem = VALUES(min_solved_problem),
                    min_user_tier = VALUES(min_user_tier),
                    min_solved_problem_tier = VALUES(min_solved_problem_tier),
                    recommendation_period = VALUES(recommendation_period),
                    updated_at = VALUES(updated_at)
            """), {
                "tag_id": tag_id_val,
                "lvl": tag_level,
                "sc": "IM",
                "mp": 0,
                "mut": immediate_user_tier,
                "mspt": immediate_highest_tier,
                "period": im_period,
                "now": now,
                "yn": True
            })

            sid = conn.execute(text(
                "SELECT tag_skill_id FROM tag_skill WHERE tag_id=:tid AND tag_skill_code=:sc"
            ), {"tid": tag_id_val, "sc": "IM"}).fetchone()[0]
            skill_id_map[(tag_id_val, "IM")] = sid

            # Advanced 삽입
            conn.execute(text("""
                INSERT INTO tag_skill (tag_id, tag_level, tag_skill_code,
                                     min_solved_problem, min_user_tier, min_solved_problem_tier,
                                     recommendation_period, created_at, updated_at, active_yn)
                VALUES (:tag_id, :lvl, :sc, :mp, :mut, :mspt, :period, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    min_solved_problem = VALUES(min_solved_problem),
                    min_user_tier = VALUES(min_user_tier),
                    min_solved_problem_tier = VALUES(min_solved_problem_tier),
                    recommendation_period = VALUES(recommendation_period),
                    updated_at = VALUES(updated_at)
            """), {
                "tag_id": tag_id_val,
                "lvl": tag_level,
                "sc": "AD",
                "mp": a_cnt,
                "mut": advanced_user_tier,
                "mspt": advanced_highest_tier,
                "period": ad_period,
                "now": now,
                "yn": True
            })

            sid = conn.execute(text(
                "SELECT tag_skill_id FROM tag_skill WHERE tag_id=:tid AND tag_skill_code=:sc"
            ), {"tid": tag_id_val, "sc": "AD"}).fetchone()[0]
            skill_id_map[(tag_id_val, "AD")] = sid

            # Master 삽입
            conn.execute(text("""
                INSERT INTO tag_skill (tag_id, tag_level, tag_skill_code,
                                     min_solved_problem, min_user_tier, min_solved_problem_tier,
                                     recommendation_period, created_at, updated_at, active_yn)
                VALUES (:tag_id, :lvl, :sc, :mp, :mut, :mspt, :period, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    min_solved_problem = VALUES(min_solved_problem),
                    min_user_tier = VALUES(min_user_tier),
                    min_solved_problem_tier = VALUES(min_solved_problem_tier),
                    recommendation_period = VALUES(recommendation_period),
                    updated_at = VALUES(updated_at)
            """), {
                "tag_id": tag_id_val,
                "lvl": tag_level,
                "sc": "MAS",
                "mp": m_cnt,
                "mut": master_user_tier,
                "mspt": master_highest_tier,
                "period": mas_period,
                "now": now,
                "yn": True
            })

            sid = conn.execute(text(
                "SELECT tag_skill_id FROM tag_skill WHERE tag_id=:tid AND tag_skill_code=:sc"
            ), {"tid": tag_id_val, "sc": "MAS"}).fetchone()[0]
            skill_id_map[(tag_id_val, "MAS")] = sid

            logger.debug(f"Created tag_skills for tag {tag_code} (id={tag_id_val}): "
                        f"IM={immediate_user_tier}, AD={advanced_user_tier}, MAS={master_user_tier}")

        self.skill_id_map = skill_id_map
        logger.info(f"Per-tag tag skills setup completed: {len(skill_id_map)} records created")

    def _setup_filters(self, conn, now):
        """문제 추천 난이도 필터 설정
        """
        logger.info("Setting up recommendation level filters...")


        filter_data = [
            ("EASY", "쉬움", None, -5, "IM", 100, 0),
            ("EASY", "쉬움", None, -5, "AD", 100, 0),
            ("EASY", "쉬움", None, -5, "MAS", 100, 0),
            ("NORMAL", "보통", None, None, "IM", 100, 50),
            ("NORMAL", "보통", None, None, "AD", 50, 20),
            ("NORMAL", "보통", None, None, "MAS", 20, 0),
            ("HARD", "어려움", None, None, "IM", 50, 30),
            ("HARD", "어려움", None, None, "AD", 20, 0),
            ("HARD", "어려움", None, None, "MAS", 10, 0),
            ("EXTREME", "매우 어려움", 2, None, "IM", 10, 0),
            ("EXTREME", "매우 어려움", 2, None, "AD", 10, 0),
            ("EXTREME", "매우 어려움", 2, None, "MAS", 10, 0)
        ]
        for f_code, d_name, min_d, max_d, code, min_rate, max_rate in filter_data:
            conn.execute(text("""
                INSERT INTO problem_recommendation_level_filter (filter_code, display_name, min_user_tier_diff, max_user_tier_diff, tag_skill_code, min_tag_skill_rate, max_tag_skill_rate, created_at, updated_at, active_yn)
                VALUES (:fc, :dn, :min, :max, :scode, :mirate, :marate, :now, :now, :yn)
                ON DUPLICATE KEY UPDATE
                    display_name = VALUES(display_name),
                    updated_at = VALUES(updated_at)
            """), {"fc": f_code, "dn": d_name, "min": min_d, "max": max_d, "scode": code, "mirate": min_rate, "marate": max_rate, "now": now, "yn": True})

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