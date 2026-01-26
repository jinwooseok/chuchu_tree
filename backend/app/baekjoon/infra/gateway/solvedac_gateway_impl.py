"""solved.ac API 데이터 수집 Gateway 구현"""

import logging
import asyncio
from datetime import datetime
import time
from typing import Any

import httpx

from app.baekjoon.domain.gateway.solvedac_gateway import SolvedacGateway
from app.baekjoon.domain.vo.solvedac_data import SolvedacUserDataVO
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)


class SolvedacGatewayImpl(SolvedacGateway):
    """solved.ac API 데이터 수집 Gateway 구현체"""

    def __init__(self, request_delay: float = 0.3, concurrent_requests: int = 3):
        self.request_delay = request_delay
        self.concurrent_requests = concurrent_requests  # 동시 요청 개수
        self.base_url = "https://solved.ac/api/v3/search/problem"
        self.user_show_url_template = "https://solved.ac/api/v3/user/show?handle={user_id}"
        self.history_url_template = "https://solved.ac/api/v3/user/history?handle={user_id}&topic=solvedCount"
        # 유저의 푼 문제를 검사할 때, API 요청 수를 줄이기 위한 로직        
        self.tag_stats_url = "https://solved.ac/api/v3/user/problem_tag_stats?handle={user_id}"
        self.level_stats_url = "https://solved.ac/api/v3/user/problem_stats?handle={user_id}"

        
    async def fetch_user_data_first(self, bj_user_id: str) -> SolvedacUserDataVO | None:
        """
        백준 유저 ID로 solved.ac에서 유저 데이터 수집 (병렬 처리)

        Args:
            bj_user_id: 백준 유저 ID (닉네임)

        Returns:
            SolvedacUserDataVO: 유저의 모든 푼 문제 및 히스토리 데이터
            None: 존재하지 않는 유저이거나 푼 문제가 없는 경우
        """
        logger.info(f"[SolvedacGateway] 유저 데이터 수집 시작: {bj_user_id}")

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # 1단계: 첫 페이지, 유저 정보, 히스토리 병렬 요청
                first_page_task = self._fetch_problem_page(client, bj_user_id, 1)
                user_info_task = self._fetch_user_info(client, bj_user_id)
                history_task = self._fetch_solve_history(client, bj_user_id)

                first_page_data, user_info_data, history_data = await asyncio.gather(
                    first_page_task,
                    user_info_task,
                    history_task
                )

                if first_page_data is None or first_page_data.get("count", 0) == 0:
                    logger.warning(f"[SolvedacGateway] 유저 '{bj_user_id}'가 푼 문제가 없거나 존재하지 않는 ID입니다.")
                    return None

                total_count = first_page_data.get("count", 0)
                all_problems = first_page_data.get("items", [])
                total_pages = (total_count - 1) // 50 + 1

                logger.info(f"[SolvedacGateway] 전체 {total_count}개 문제 발견 ({total_pages} 페이지)")

                # 2단계: 나머지 페이지들 병렬 요청
                if total_pages > 1:
                    all_problems.extend(
                        await self._fetch_remaining_pages_parallel(client, bj_user_id, total_pages)
                    )

                # VO로 변환
                result = {
                    "user_id": bj_user_id,
                    "count": len(all_problems),
                    "total_count": total_count,
                    "items": all_problems,
                    "user_info": user_info_data,
                    "history": history_data,
                    "collected_at": datetime.now().isoformat()
                }

                user_data = SolvedacUserDataVO.from_collector_response(result)
                logger.info(f"[SolvedacGateway] 데이터 수집 완료: {user_data.total_count}개 문제, {len(user_data.history)}개 히스토리")
                return user_data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"[SolvedacGateway] 존재하지 않는 유저: {bj_user_id}")
                return None
            logger.error(f"[SolvedacGateway] HTTP 에러: {e}")
            raise APIException(ErrorCode.EXTERNAL_API_ERROR)
        except httpx.RequestError as e:
            logger.error(f"[SolvedacGateway] 요청 에러: {e}")
            raise APIException(ErrorCode.EXTERNAL_API_ERROR)
        except Exception as e:
            logger.error(f"[SolvedacGateway] 예상치 못한 에러: {e}")
            raise APIException(ErrorCode.INTERNAL_SERVER_ERROR)
    
    async def fetch_user_data(self, bj_user_id: str, original_solved_data) -> SolvedacUserDataVO | None:
        raise NotImplementedError
    #     try:
    #         async with httpx.AsyncClient(timeout=30.0) as client:
    #             # 1단계: 첫 페이지, 유저 정보, 히스토리 병렬 요청
    #             user_info_task = self._fetch_user_info(client, bj_user_id)
    #             tag_stat_task = self._get_tag_stats(client, bj_user_id)
    #             level_stat_task = self._get_level_stats(client, bj_user_id)
                
    #             user_info_data, tag_stat_data, level_stat_data = await asyncio.gather(
    #                 user_info_task, tag_stat_task, level_stat_task
    #             )
                
    #             self.check_update(original_solved_data, tag_stat_data, level_stat_data)
                
    #             # VO로 변환
    #             result = {
    #                 "user_id": bj_user_id,
    #                 "count": len(changed_problems),
    #                 "total_count": total_count,
    #                 "items": changed_problems,
    #                 "user_info": user_info_data,
    #                 "history": changed_history_data,
    #                 "collected_at": datetime.now().isoformat()
    #             }

    #             user_data = SolvedacUserDataVO.from_collector_response(result)
    #             logger.info(f"[SolvedacGateway] 데이터 수집 완료: {user_data.total_count}개 문제, {len(user_data.history)}개 히스토리")
    #             return user_data

    #     except httpx.HTTPStatusError as e:
    #         if e.response.status_code == 404:
    #             logger.warning(f"[SolvedacGateway] 존재하지 않는 유저: {bj_user_id}")
    #             return None
    #         logger.error(f"[SolvedacGateway] HTTP 에러: {e}")
    #         raise APIException(ErrorCode.EXTERNAL_API_ERROR)
    #     except httpx.RequestError as e:
    #         logger.error(f"[SolvedacGateway] 요청 에러: {e}")
    #         raise APIException(ErrorCode.EXTERNAL_API_ERROR)
    #     except Exception as e:
    #         logger.error(f"[SolvedacGateway] 예상치 못한 에러: {e}")
    #         raise APIException(ErrorCode.INTERNAL_SERVER_ERROR)
    
    def _get_tag_stats(self, client) -> list[dict]:
        """유저가 푼 태그별 문제 수 수집"""
        try:
            response = client.get(self.tag_stats_url)
            response.raise_for_status()
            data = response.json()
            return data.get("items", [])
        except client.exceptions.RequestException as e:
            print(f"[업데이트기] 태그 통계 에러: {e}")
            return []
        
    def _get_level_stats(self, client) -> list[dict]:
        """유저가 푼 티어별 문제 수 수집"""
        try:
            response = client.get(self.level_stats_url)
            response.raise_for_status()
            data = response.json()
            # level_stats API는 리스트를 직접 반환
            return data if isinstance(data, list) else []
        except client.exceptions.RequestException as e:
            print(f"[업데이트기] 티어 통계 에러: {e}")
            return []
    
    def check_update(self, solved_stat_data: dict | None, tag_stat_data, level_stat_task) -> dict[str, Any]:
        """
        변경사항 확인 및 업데이트

        Args:
            cached_data: 이전에 저장된 데이터 (tag_stats, level_stats 포함)
        """
        print(f"[업데이트기] 시작 (유저: {self.user_id})...")
        start_time = time.time()

        # 태그별 통계 수집
        tag_stats = tag_stat_data

        # 티어별 통계 수집
        level_stats = level_stat_task

        result = {
            "user_id": self.user_id,
            "tag_stats": tag_stats,
            "level_stats": level_stats,
            "checked_at": datetime.now().isoformat(),
            "has_changes": False
        }

        # 캐시된 데이터와 비교
        if solved_stat_data:
            old_tag_stats = {item["tag"]["key"]: item["solved"] for item in solved_stat_data.get("tag_stats", [])}
            new_tag_stats = {item["tag"]["key"]: item["solved"] for item in tag_stats}

            old_level_stats = {item["level"]: item["solved"] for item in solved_stat_data.get("level_stats", [])}
            new_level_stats = {item["level"]: item["solved"] for item in level_stats}

            tag_changes = {k: v for k, v in new_tag_stats.items() if old_tag_stats.get(k, 0) != v}
            level_changes = {k: v for k, v in new_level_stats.items() if old_level_stats.get(k, 0) != v}

            if tag_changes or level_changes:
                result["has_changes"] = True
                result["tag_changes"] = tag_changes
                result["level_changes"] = level_changes
                print(f"[업데이트기] 변경 감지: 태그 {len(tag_changes)}개, 티어 {len(level_changes)}개")
            else:
                print(f"[업데이트기] 변경사항 없음")
        else:
            print(f"[업데이트기] 첫 수집 - 태그 {len(tag_stats)}개, 티어 {len(level_stats)}개")

        elapsed = time.time() - start_time
        print(f"[업데이트기] 완료 (소요시간: {elapsed:.2f}초)")

        return result
    
    async def _fetch_problem_page(self, client: httpx.AsyncClient, user_id: str, page: int) -> dict[str, Any] | None:
        """문제 목록 단일 페이지 요청"""
        query = f"solved_by:{user_id}"
        response = await client.get(f"{self.base_url}?query={query}&page={page}")
        response.raise_for_status()
        return response.json()

    async def _fetch_remaining_pages_parallel(
        self,
        client: httpx.AsyncClient,
        user_id: str,
        total_pages: int
    ) -> list[dict]:
        """나머지 페이지들을 병렬로 수집"""
        all_problems = []

        # concurrent_requests 개씩 묶어서 병렬 요청
        for batch_start in range(2, total_pages + 1, self.concurrent_requests):
            batch_end = min(batch_start + self.concurrent_requests, total_pages + 1)
            pages_to_fetch = range(batch_start, batch_end)

            # 딜레이 후 병렬 요청
            await asyncio.sleep(self.request_delay)

            tasks = [
                self._fetch_problem_page(client, user_id, page)
                for page in pages_to_fetch
            ]

            batch_results = await asyncio.gather(*tasks)

            for result in batch_results:
                if result:
                    all_problems.extend(result.get("items", []))

            current_page = batch_end - 1
            logger.info(f"[SolvedacGateway] 진행 중... {current_page}/{total_pages} 페이지")

        return all_problems

    async def _fetch_user_info(self, client: httpx.AsyncClient, user_id: str) -> dict:
        """유저 정보 수집 (user/show API)"""
        try:
            url = self.user_show_url_template.format(user_id=user_id)
            response = await client.get(url)
            response.raise_for_status()
            user_info = response.json()

            logger.info(f"[SolvedacGateway] 유저 정보 수집 완료: tier={user_info.get('tier')}, rating={user_info.get('rating')}")
            return user_info

        except Exception as e:
            logger.warning(f"[SolvedacGateway] 유저 정보 수집 실패: {e}")
            return {}

    async def _fetch_solve_history(self, client: httpx.AsyncClient, user_id: str) -> list[dict]:
        """유저의 문제 해결 히스토리 수집"""
        try:
            await asyncio.sleep(self.request_delay)
            url = self.history_url_template.format(user_id=user_id)
            response = await client.get(url)
            response.raise_for_status()
            history_data = response.json()

            if isinstance(history_data, list):
                logger.info(f"[SolvedacGateway] 히스토리 {len(history_data)}개 항목 수집")
                return history_data
            return []

        except Exception as e:
            logger.warning(f"[SolvedacGateway] 히스토리 수집 실패: {e}")
            return []
