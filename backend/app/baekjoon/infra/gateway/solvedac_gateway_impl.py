"""solved.ac API 데이터 수집 Gateway 구현"""

import logging
import asyncio
from datetime import datetime
from typing import Any

import httpx

from app.baekjoon.domain.gateway.solvedac_gateway import SolvedacGateway
from app.baekjoon.domain.vo.solvedac_data import SolvedacUserDataVO
from app.core.error_codes import ErrorCode
from app.core.exception import APIException

logger = logging.getLogger(__name__)


class SolvedacGatewayImpl(SolvedacGateway):
    """solved.ac API 데이터 수집 Gateway 구현체"""

    def __init__(self, request_delay: float = 0.3, concurrent_requests: int = 5):
        self.request_delay = request_delay
        self.concurrent_requests = concurrent_requests  # 동시 요청 개수
        self.base_url = "https://solved.ac/api/v3/search/problem"
        self.user_show_url_template = "https://solved.ac/api/v3/user/show?handle={user_id}"
        self.history_url_template = "https://solved.ac/api/v3/user/history?handle={user_id}&topic=solvedCount"

    async def fetch_user_data(self, bj_user_id: str) -> SolvedacUserDataVO | None:
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
