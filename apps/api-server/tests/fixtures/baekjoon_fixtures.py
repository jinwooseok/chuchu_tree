"""
백준 테스트를 위한 중앙화된 픽스처 및 모킹 데이터

이 모듈은 백준 계정 연동 및 츄츄트리 업데이트 테스트를 위한
모든 모킹 데이터와 생성 함수를 제공합니다.
"""

from datetime import datetime, timedelta
from typing import List, Dict, Any


# ============================================================================
# Tier 상수
# ============================================================================

TIER_UNRATED = 0
TIER_BRONZE_V = 1
TIER_BRONZE_IV = 2
TIER_BRONZE_III = 3
TIER_BRONZE_II = 4
TIER_BRONZE_I = 5
TIER_SILVER_V = 6
TIER_SILVER_IV = 7
TIER_SILVER_III = 8
TIER_SILVER_II = 9
TIER_SILVER_I = 10
TIER_GOLD_V = 11
TIER_GOLD_IV = 12
TIER_GOLD_III = 13
TIER_GOLD_II = 14
TIER_GOLD_I = 15
TIER_PLATINUM_V = 16
TIER_PLATINUM_IV = 17
TIER_PLATINUM_III = 18
TIER_PLATINUM_II = 19
TIER_PLATINUM_I = 20


# ============================================================================
# solved.ac 사용자 정보 모킹 응답
# ============================================================================

MOCK_USER_BRONZE = {
    "handle": "bronze_user",
    "tier": TIER_BRONZE_V,
    "rating": 500,
    "class": 1,
    "solvedCount": 20,
    "rank": 50000,
    "maxStreak": 5
}

MOCK_USER_SILVER = {
    "handle": "silver_user",
    "tier": TIER_SILVER_III,
    "rating": 900,
    "class": 2,
    "solvedCount": 100,
    "rank": 30000,
    "maxStreak": 15
}

MOCK_USER_GOLD = {
    "handle": "gold_user",
    "tier": TIER_GOLD_V,
    "rating": 1500,
    "class": 3,
    "solvedCount": 234,
    "rank": 12345,
    "maxStreak": 30
}

MOCK_USER_PLATINUM = {
    "handle": "platinum_user",
    "tier": TIER_PLATINUM_III,
    "rating": 2100,
    "class": 5,
    "solvedCount": 567,
    "rank": 3456,
    "maxStreak": 50
}

# 테스트용 기본 사용자
MOCK_USER_DEFAULT = MOCK_USER_GOLD


# ============================================================================
# 데이터 생성 함수
# ============================================================================

def generate_mock_problems(count: int, start_id: int = 1000, base_date: datetime = None) -> List[Dict[str, Any]]:
    """
    solved.ac API 응답 형식과 일치하는 모킹 문제 리스트 생성

    Args:
        count: 생성할 문제 개수
        start_id: 시작 문제 ID
        base_date: 기준 날짜 (None이면 현재 시간 사용)

    Returns:
        문제 리스트 (solved.ac API 형식)
    """
    if base_date is None:
        base_date = datetime.utcnow()

    problems = []
    tags_pool = [
        {"bojTagId": 124, "key": "arithmetic", "displayNames": [{"language": "ko", "name": "사칙연산"}]},
        {"bojTagId": 125, "key": "dp", "displayNames": [{"language": "ko", "name": "다이나믹 프로그래밍"}]},
        {"bojTagId": 126, "key": "greedy", "displayNames": [{"language": "ko", "name": "그리디 알고리즘"}]},
        {"bojTagId": 127, "key": "implementation", "displayNames": [{"language": "ko", "name": "구현"}]},
        {"bojTagId": 128, "key": "graphs", "displayNames": [{"language": "ko", "name": "그래프 이론"}]},
        {"bojTagId": 129, "key": "data_structures", "displayNames": [{"language": "ko", "name": "자료 구조"}]},
        {"bojTagId": 130, "key": "math", "displayNames": [{"language": "ko", "name": "수학"}]},
        {"bojTagId": 131, "key": "string", "displayNames": [{"language": "ko", "name": "문자열"}]},
        {"bojTagId": 132, "key": "bruteforcing", "displayNames": [{"language": "ko", "name": "브루트포스 알고리즘"}]},
        {"bojTagId": 133, "key": "sorting", "displayNames": [{"language": "ko", "name": "정렬"}]},
    ]

    for i in range(count):
        problem_id = start_id + i
        level = (i % 30) + 1  # 레벨 1-30
        tag = tags_pool[i % len(tags_pool)]
        solved_at = base_date - timedelta(days=i, hours=i % 24)

        problems.append({
            "problemId": problem_id,
            "titleKo": f"문제 {problem_id}",
            "titleEn": f"Problem {problem_id}",
            "level": level,
            "tags": [tag],
            "solvedAt": solved_at.isoformat() + "Z"
        })

    return problems


def generate_streak_data(current: int, longest: int, last_solved: datetime = None) -> Dict[str, Any]:
    """
    solved.ac API 응답 형식과 일치하는 스트릭 데이터 생성

    Args:
        current: 현재 스트릭
        longest: 최장 스트릭
        last_solved: 마지막으로 문제를 푼 시간

    Returns:
        스트릭 데이터 (solved.ac API 형식)
    """
    if last_solved is None:
        last_solved = datetime.utcnow()

    return {
        "currentStreak": current,
        "longestStreak": longest,
        "lastSolvedAt": last_solved.isoformat() + "Z",
        "totalSolved": current + 100  # 예시 값
    }


def generate_user_history(days: int, base_date: datetime = None) -> List[Dict[str, Any]]:
    """
    solved.ac API 응답 형식과 일치하는 사용자 히스토리 생성

    Args:
        days: 생성할 일수
        base_date: 기준 날짜

    Returns:
        히스토리 리스트 (solved.ac API 형식)
    """
    if base_date is None:
        base_date = datetime.utcnow()

    history = []
    for i in range(days):
        date = base_date - timedelta(days=i)
        solved_count = (i % 5) + 1  # 하루에 1-5문제 푼 것으로 가정

        history.append({
            "timestamp": date.isoformat().replace('+00:00', 'Z'),
            "solvedCount": solved_count
        })

    return history


def create_solvedac_user_data_vo(
    user_id: str,
    tier: int = TIER_GOLD_V,
    rating: int = 1500,
    class_level: int = 3,
    solved_count: int = 100,
    max_streak: int = 30,
    problem_count: int = 100,
    current_streak: int = 15
) -> Dict[str, Any]:
    """
    SolvedacUserDataVO 형식의 완전한 사용자 데이터 생성

    Args:
        user_id: 백준 사용자 ID
        tier: 티어 (1-30)
        rating: 레이팅
        class_level: 클래스 레벨
        solved_count: 푼 문제 수
        max_streak: 최장 스트릭
        problem_count: 반환할 문제 개수
        current_streak: 현재 스트릭

    Returns:
        SolvedacUserDataVO 형식의 딕셔너리
    """
    from unittest.mock import MagicMock

    # UserInfo 모킹
    user_info = MagicMock()
    user_info.tier = tier
    user_info.rating = rating
    user_info.class_level = class_level
    user_info.max_streak = max_streak
    user_info.solved_count = solved_count

    # 문제 리스트 생성
    problems_data = generate_mock_problems(problem_count)
    problems = []
    for p in problems_data:
        problem = MagicMock()
        problem.problem_id = p["problemId"]
        problem.title = p["titleKo"]
        problem.level = p["level"]
        problem.tags = p["tags"]
        problems.append(problem)

    # 히스토리 생성
    history_data = generate_user_history(current_streak)
    history = []
    for h in history_data:
        hist_item = MagicMock()
        hist_item.timestamp = h["timestamp"]
        hist_item.solved_count = h["solvedCount"]
        history.append(hist_item)

    # 전체 데이터
    user_data = MagicMock()
    user_data.user_id = user_id
    user_data.user_info = user_info
    user_data.total_count = solved_count
    user_data.problems = problems
    user_data.history = history
    user_data.collected_at = datetime.utcnow()

    return user_data


# ============================================================================
# 에러 시나리오 응답
# ============================================================================

SOLVEDAC_API_ERROR_RESPONSES = {
    "user_not_found": {
        "status": 404,
        "message": "User not found on solved.ac"
    },
    "service_unavailable": {
        "status": 503,
        "message": "solved.ac service is temporarily unavailable"
    },
    "rate_limited": {
        "status": 429,
        "message": "Too many requests. Please try again later."
    },
    "timeout": {
        "error": "Request timeout after 30 seconds"
    },
    "internal_server_error": {
        "status": 500,
        "message": "Internal server error from solved.ac"
    }
}


# ============================================================================
# 업데이트 시나리오용 데이터
# ============================================================================

def create_update_scenario_data(
    existing_problem_count: int = 100,
    new_problem_count: int = 5,
    tier_change: int = 0,
    streak_change: int = 0
) -> Dict[str, Any]:
    """
    업데이트 테스트를 위한 시나리오 데이터 생성

    Args:
        existing_problem_count: 기존 문제 수
        new_problem_count: 새로 추가된 문제 수
        tier_change: 티어 변화 (+1: 승급, -1: 강등, 0: 변화 없음)
        streak_change: 스트릭 변화

    Returns:
        업데이트 시나리오 데이터
    """
    base_tier = TIER_GOLD_V
    base_streak = 15

    # 기존 문제 IDs
    existing_problem_ids = list(range(1000, 1000 + existing_problem_count))

    # 전체 문제 (기존 + 신규)
    total_problem_count = existing_problem_count + new_problem_count
    all_problems = generate_mock_problems(total_problem_count, start_id=1000)

    # 새로운 문제 IDs
    new_problem_ids = list(range(1000 + existing_problem_count, 1000 + total_problem_count))

    # 업데이트된 티어
    updated_tier = base_tier + tier_change

    # 업데이트된 스트릭
    updated_streak = base_streak + streak_change

    return {
        "existing_problem_ids": existing_problem_ids,
        "new_problem_ids": new_problem_ids,
        "all_problems": all_problems,
        "base_tier": base_tier,
        "updated_tier": updated_tier,
        "base_streak": base_streak,
        "updated_streak": updated_streak,
        "new_problem_count": new_problem_count
    }


# ============================================================================
# 계정 링크 시나리오용 데이터
# ============================================================================

def create_link_scenario_data(
    user_id: str = "test_user",
    tier: int = TIER_GOLD_V,
    problem_count: int = 50
) -> Dict[str, Any]:
    """
    계정 연동 테스트를 위한 시나리오 데이터 생성

    Args:
        user_id: 백준 사용자 ID
        tier: 티어
        problem_count: 문제 수

    Returns:
        계정 연동 시나리오 데이터
    """
    return {
        "user_id": user_id,
        "tier": tier,
        "rating": 1500 + (tier - TIER_GOLD_V) * 100,
        "class_level": 3,
        "solved_count": problem_count,
        "max_streak": 30,
        "problems": generate_mock_problems(problem_count),
        "current_streak": 15,
        "history": generate_user_history(15)
    }
