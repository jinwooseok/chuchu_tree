"""
solved.ac API 수집기 메인 실행 파일

사용법:
    python main.py

유저 ID 변경:
    스크립트 상단의 USER_ID 변수를 수정하세요.
"""

import concurrent.futures
import time
from datetime import datetime

from solvedac_tag_collector import TagCollector
from solvedac_problem_collector import ProblemCollector
from solvedac_first_status_collector import FirstStatusCollector
from solvedac_solved_problem_updater import SolvedProblemUpdater


# ============================================
# 설정 (여기서 유저 ID를 변경하세요)
# ============================================
USER_ID = "jinus7949"

# API 요청 간격 (초)
PROBLEM_COLLECTOR_DELAY = 0.5  # 문제 수집기
TAG_COLLECTOR_DELAY = 0.5      # 태그 수집기
UPDATER_DELAY = 0.3            # 업데이트기
FIRST_STATUS_DELAY = 0.3       # 첫 데이터 수집기


def run_tag_collector():
    """태그 수집기 실행"""
    collector = TagCollector(delay=TAG_COLLECTOR_DELAY)
    data = collector.collect()
    collector.save_to_json(data)
    return data


def run_problem_collector(max_pages=None):
    """
    문제 수집기 실행

    Args:
        max_pages: 테스트용 최대 페이지 (None이면 전체)
    """
    collector = ProblemCollector(delay=PROBLEM_COLLECTOR_DELAY)
    data = collector.collect(max_pages=max_pages)
    collector.save_to_json(data)
    return data


def run_first_status_collector(user_id=USER_ID):
    """첫 데이터 수집기 실행"""
    collector = FirstStatusCollector(user_id, delay=FIRST_STATUS_DELAY)
    data = collector.collect()
    collector.save_to_json(data)
    return data


def run_updater(user_id=USER_ID):
    """업데이트기 실행"""
    updater = SolvedProblemUpdater(user_id, delay=UPDATER_DELAY)
    cached_data = updater.load_cached_data()

    if cached_data:
        print(f"[메인] 캐시된 데이터 발견 - 변경사항 확인")

    data = updater.check_update(cached_data)
    updater.save_to_json(data)
    return data


def run_parallel_meta_collectors(max_problem_pages=None):
    """
    메타 데이터 수집기 병렬 실행 (문제 + 태그)

    Args:
        max_problem_pages: 문제 수집기 테스트용 최대 페이지
    """
    print("\n" + "="*60)
    print("메타 데이터 수집 시작 (문제 + 태그) - 병렬 실행")
    print("="*60)

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_problems = executor.submit(run_problem_collector, max_problem_pages)
        future_tags = executor.submit(run_tag_collector)

        problems_data = future_problems.result()
        tags_data = future_tags.result()

    elapsed = time.time() - start_time
    print(f"\n메타 데이터 수집 완료 (총 소요시간: {elapsed:.2f}초)")

    return {
        "problems": problems_data,
        "tags": tags_data
    }


def run_parallel_user_collectors(user_id=USER_ID):
    """
    유저 데이터 수집기 병렬 실행 (첫 데이터 수집 + 업데이트)

    주의: 일반적으로는 첫 데이터 수집과 업데이트를 동시에 실행하지 않습니다.
          이 함수는 테스트용입니다.
    """
    print("\n" + "="*60)
    print(f"유저 데이터 수집 시작 (유저: {user_id}) - 병렬 실행")
    print("="*60)

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_first = executor.submit(run_first_status_collector, user_id)
        future_update = executor.submit(run_updater, user_id)

        first_data = future_first.result()
        update_data = future_update.result()

    elapsed = time.time() - start_time
    print(f"\n유저 데이터 수집 완료 (총 소요시간: {elapsed:.2f}초)")

    return {
        "first_status": first_data,
        "update": update_data
    }


def run_all_parallel(user_id=USER_ID, max_problem_pages=None):
    """
    모든 수집기 병렬 실행

    Args:
        user_id: 유저 ID
        max_problem_pages: 문제 수집기 테스트용 최대 페이지
    """
    print("\n" + "="*60)
    print("전체 수집기 병렬 실행")
    print(f"유저 ID: {user_id}")
    print(f"시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    start_time = time.time()

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_problems = executor.submit(run_problem_collector, max_problem_pages)
        future_tags = executor.submit(run_tag_collector)
        future_first = executor.submit(run_first_status_collector, user_id)
        future_update = executor.submit(run_updater, user_id)

        problems_data = future_problems.result()
        tags_data = future_tags.result()
        first_data = future_first.result()
        update_data = future_update.result()

    elapsed = time.time() - start_time
    print("\n" + "="*60)
    print("전체 수집 완료")
    print(f"총 소요시간: {elapsed:.2f}초")
    print(f"종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    return {
        "problems": problems_data,
        "tags": tags_data,
        "first_status": first_data,
        "update": update_data
    }


def main():
    """메인 함수"""
    print("="*60)
    print("solved.ac API 수집기")
    print("="*60)
    print("\n실행 옵션을 선택하세요:")
    print("1. 태그 수집기만 실행")
    print("2. 문제 수집기만 실행 (테스트: 2페이지)")
    print("3. 첫 데이터 수집기만 실행")
    print("4. 업데이트기만 실행")
    print("5. 메타 데이터 수집 병렬 실행 (문제 + 태그)")
    print("6. 유저 데이터 수집 병렬 실행 (첫 데이터 + 업데이트)")
    print("7. 전체 수집기 병렬 실행")
    print("8. 문제 수집기 전체 실행 (주의: 시간 오래 걸림)")

    choice = input("\n선택 (1-8): ").strip()

    if choice == "1":
        run_tag_collector()
    elif choice == "2":
        run_problem_collector(max_pages=2)
    elif choice == "3":
        run_first_status_collector()
    elif choice == "4":
        run_updater()
    elif choice == "5":
        run_parallel_meta_collectors(max_problem_pages=2)
    elif choice == "6":
        run_parallel_user_collectors()
    elif choice == "7":
        run_all_parallel(max_problem_pages=2)
    elif choice == "8":
        confirm = input("전체 문제를 수집하면 시간이 오래 걸립니다. 계속하시겠습니까? (y/n): ")
        if confirm.lower() == "y":
            run_problem_collector(max_pages=None)
        else:
            print("취소되었습니다.")
    else:
        print("잘못된 선택입니다.")


if __name__ == "__main__":
    main()

# https://solved.ac/api/v3/user/show?handle=jinus7949