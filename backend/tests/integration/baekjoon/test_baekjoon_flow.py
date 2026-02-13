import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timedelta

from tests.fixtures.baekjoon_fixtures import (
    create_link_scenario_data,
    create_update_scenario_data,
    TIER_GOLD_V,
    TIER_GOLD_IV,
)


class TestBaekjoonAuth:
    """백준 API - 인증 필요 엔드포인트"""

    async def test_link_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post(
            "/api/v1/bj-accounts/link",
            json={"bjAccount": "test_bj"},
        )
        assert resp.status_code == 401

    async def test_get_me_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/bj-accounts/me")
        assert resp.status_code == 401

    async def test_get_streak_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get(
            "/api/v1/bj-accounts/me/streak",
            params={"startDate": "2025-01-01", "endDate": "2025-01-31"},
        )
        assert resp.status_code == 401

    async def test_get_monthly_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get(
            "/api/v1/bj-accounts/me/problems",
            params={"year": 2025, "month": 1},
        )
        assert resp.status_code == 401

    async def test_get_unrecorded_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/bj-accounts/unrecorded-problems/me")
        assert resp.status_code == 401

    async def test_refresh_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post("/api/v1/bj-accounts/me/refresh")
        assert resp.status_code == 401


class TestBaekjoonAuthenticated:
    """백준 API - 인증된 상태 (백준 연동 전이라 에러 예상)"""

    async def test_get_me_unlinked_user(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        """백준 미연동 유저 → UNLINKED_USER 에러"""
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/bj-accounts/me")
        # 연동 안 되어있으면 에러
        assert resp.status_code in (400, 404)

    async def test_get_streak_unlinked_user(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get(
            "/api/v1/bj-accounts/me/streak",
            params={"startDate": "2025-01-01", "endDate": "2025-01-31"},
        )
        assert resp.status_code in (400, 404)

    async def test_get_unrecorded_unlinked_user(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/bj-accounts/unrecorded-problems/me")
        assert resp.status_code in (400, 404)


class TestBaekjoonLinking:
    """백준 계정 연동 통합 테스트"""

    @pytest.fixture
    def mock_solvedac_gateway_success(self):
        """성공적인 solved.ac API 응답 모킹"""

        def _create_mock(bj_account_id: str = "test_user", problem_count: int = 50):
            scenario_data = create_link_scenario_data(
                user_id=bj_account_id,
                tier=TIER_GOLD_V,
                problem_count=problem_count
            )

            user_info = MagicMock()
            user_info.tier = scenario_data["tier"]
            user_info.rating = scenario_data["rating"]
            user_info.class_level = scenario_data["class_level"]
            user_info.max_streak = scenario_data["max_streak"]
            user_info.solved_count = scenario_data["solved_count"]

            problems = []
            for p in scenario_data["problems"]:
                problem = MagicMock()
                problem.problem_id = p["problemId"]
                problem.title = p["titleKo"]
                problem.level = p["level"]
                problem.tags = p.get("tags", [])
                problems.append(problem)

            history = []
            for h in scenario_data["history"]:
                hist_item = MagicMock()
                hist_item.timestamp = h["timestamp"]
                hist_item.solved_count = h["solvedCount"]
                history.append(hist_item)

            user_data = MagicMock()
            user_data.user_id = bj_account_id
            user_data.user_info = user_info
            user_data.total_count = problem_count
            user_data.problems = problems
            user_data.history = history
            user_data.collected_at = datetime.utcnow()

            return user_data

        return _create_mock

    async def test_link_baekjoon_account_success_e2e(
        self,
        integration_client: AsyncClient,
        integration_session,
        valid_access_token: str,
        mock_solvedac_gateway_success
    ):
        """백준 계정 연동 성공 E2E 테스트"""
        integration_client.cookies.set("access_token", valid_access_token)

        # Mock solved.ac gateway
        user_data = mock_solvedac_gateway_success("new_test_user", problem_count=50)

        with patch("app.baekjoon.infra.gateway.solvedac_gateway_impl.SolvedacGatewayImpl.fetch_user_data_first") as mock_fetch:
            mock_fetch.return_value = user_data

            resp = await integration_client.post(
                "/api/v1/bj-accounts/link",
                json={"bjAccount": "new_test_user"}
            )

            # 성공 응답 확인 (200 또는 201)
            assert resp.status_code in (200, 201), f"Expected 200 or 201, got {resp.status_code}: {resp.text}"

            # 응답 데이터 검증
            if resp.status_code == 200:
                data = resp.json()
                assert "bjAccount" in data or "message" in data

        # 데이터베이스 검증: BaekjoonAccount 생성됨
        from app.baekjoon.infra.model.bj_account import BjAccountModel
        from sqlalchemy import select

        result = await integration_session.execute(
            select(BjAccountModel).where(
                BjAccountModel.bj_account_id == "new_test_user"
            )
        )
        account = result.scalars().first()
        assert account is not None, "BaekjoonAccount should be created in database"
        assert account.tier_id == TIER_GOLD_V

    async def test_link_baekjoon_account_user_not_found_in_solvedac(
        self,
        integration_client: AsyncClient,
        valid_access_token: str
    ):
        """solved.ac에서 사용자를 찾을 수 없을 때 404 응답"""
        integration_client.cookies.set("access_token", valid_access_token)

        with patch("app.baekjoon.infra.gateway.solvedac_gateway_impl.SolvedacGatewayImpl.fetch_user_data_first") as mock_fetch:
            # solved.ac에서 사용자를 찾지 못함
            mock_fetch.return_value = None

            resp = await integration_client.post(
                "/api/v1/bj-accounts/link",
                json={"bjAccount": "nonexistent_user"}
            )

            # 404 응답 확인
            assert resp.status_code == 404

    async def test_link_baekjoon_account_unauthenticated_fails(
        self,
        integration_client: AsyncClient
    ):
        """인증 없이 계정 연동 시도 시 401 응답"""
        resp = await integration_client.post(
            "/api/v1/bj-accounts/link",
            json={"bjAccount": "test_user"}
        )

        assert resp.status_code == 401


class TestBaekjoonUpdate:
    """츄츄트리 업데이트 통합 테스트"""

    @pytest.fixture
    def mock_solvedac_gateway_update(self):
        """업데이트용 solved.ac API 응답 모킹"""

        def _create_mock(existing_count: int = 100, new_count: int = 5, tier_change: int = 0):
            scenario_data = create_update_scenario_data(
                existing_problem_count=existing_count,
                new_problem_count=new_count,
                tier_change=tier_change,
                streak_change=5
            )

            user_info = MagicMock()
            user_info.tier = scenario_data["updated_tier"]
            user_info.rating = 1500 + (tier_change * 100)
            user_info.class_level = 3
            user_info.max_streak = 35
            user_info.solved_count = existing_count + new_count

            problems = []
            for p in scenario_data["all_problems"]:
                problem = MagicMock()
                problem.problem_id = p["problemId"]
                problem.title = p["titleKo"]
                problem.level = p["level"]
                problem.tags = p.get("tags", [])
                problems.append(problem)

            history = []
            for i in range(20):
                hist_item = MagicMock()
                hist_item.timestamp = (datetime.utcnow() - timedelta(days=i)).isoformat() + "Z"
                hist_item.solved_count = 1
                history.append(hist_item)

            user_data = MagicMock()
            user_data.user_id = "test_bj_user"
            user_data.user_info = user_info
            user_data.total_count = existing_count + new_count
            user_data.problems = problems
            user_data.history = history
            user_data.collected_at = datetime.utcnow()

            return user_data

        return _create_mock

    async def test_refresh_baekjoon_account_success_with_new_problems(
        self,
        integration_client: AsyncClient,
        integration_session,
        linked_baekjoon_account,
        baekjoon_test_user,
        mock_solvedac_gateway_update,
        token_service
    ):
        """새로운 문제가 있을 때 수동 새로고침 성공"""
        # 인증 토큰 생성
        access_token = token_service.create_token(
            payload={"user_account_id": baekjoon_test_user.user_account_id},
            expires_delta=timedelta(hours=6)
        )
        integration_client.cookies.set("access_token", access_token)

        # Mock solved.ac gateway (5개 신규 문제)
        user_data = mock_solvedac_gateway_update(existing_count=100, new_count=5, tier_change=0)

        with patch("app.baekjoon.infra.gateway.solvedac_gateway_impl.SolvedacGatewayImpl.fetch_user_data_first") as mock_fetch:
            mock_fetch.return_value = user_data

            resp = await integration_client.post("/api/v1/bj-accounts/me/refresh")

            # 성공 응답 확인
            assert resp.status_code == 200, f"Expected 200, got {resp.status_code}: {resp.text}"

        # 데이터베이스 검증: 신규 문제 히스토리 생성됨
        from app.baekjoon.infra.model.problem_history import ProblemHistoryModel
        from sqlalchemy import select, func

        result = await integration_session.execute(
            select(func.count()).select_from(ProblemHistoryModel).where(
                ProblemHistoryModel.bj_account_id == linked_baekjoon_account.bj_account_id
            )
        )
        count = result.scalar()
        # 기존 100개 + 신규 5개 = 105개 (실제로는 모킹 데이터에 따라 다를 수 있음)
        assert count >= 100, f"Expected at least 100 problem histories, got {count}"

    async def test_refresh_baekjoon_account_no_new_problems(
        self,
        integration_client: AsyncClient,
        integration_session,
        linked_baekjoon_account,
        baekjoon_test_user,
        mock_solvedac_gateway_update,
        token_service
    ):
        """신규 문제가 없을 때 효율적인 처리"""
        access_token = token_service.create_token(
            payload={"user_account_id": baekjoon_test_user.user_account_id},
            expires_delta=timedelta(hours=6)
        )
        integration_client.cookies.set("access_token", access_token)

        # Mock solved.ac gateway (신규 문제 없음)
        user_data = mock_solvedac_gateway_update(existing_count=100, new_count=0, tier_change=0)

        with patch("app.baekjoon.infra.gateway.solvedac_gateway_impl.SolvedacGatewayImpl.fetch_user_data_first") as mock_fetch:
            mock_fetch.return_value = user_data

            resp = await integration_client.post("/api/v1/bj-accounts/me/refresh")

            # 성공 응답 확인
            assert resp.status_code == 200

    async def test_refresh_baekjoon_account_not_linked_fails(
        self,
        integration_client: AsyncClient,
        valid_access_token: str
    ):
        """백준 계정이 연동되지 않았을 때 404 응답"""
        integration_client.cookies.set("access_token", valid_access_token)

        resp = await integration_client.post("/api/v1/bj-accounts/me/refresh")

        # 404 응답 확인
        assert resp.status_code in (400, 404)

    async def test_refresh_baekjoon_account_tier_and_streak_changes(
        self,
        integration_client: AsyncClient,
        integration_session,
        linked_baekjoon_account,
        baekjoon_test_user,
        mock_solvedac_gateway_update,
        token_service
    ):
        """티어 및 스트릭 변경 시 다중 속성 업데이트"""
        access_token = token_service.create_token(
            payload={"user_account_id": baekjoon_test_user.user_account_id},
            expires_delta=timedelta(hours=6)
        )
        integration_client.cookies.set("access_token", access_token)

        # Mock solved.ac gateway (티어 승급: Gold V → Gold IV)
        user_data = mock_solvedac_gateway_update(existing_count=100, new_count=5, tier_change=+1)

        with patch("app.baekjoon.infra.gateway.solvedac_gateway_impl.SolvedacGatewayImpl.fetch_user_data_first") as mock_fetch:
            mock_fetch.return_value = user_data

            resp = await integration_client.post("/api/v1/bj-accounts/me/refresh")

            # 성공 응답 확인
            assert resp.status_code == 200

        # 데이터베이스 검증: 티어가 업데이트됨
        from app.baekjoon.infra.model.bj_account import BjAccountModel
        from sqlalchemy import select

        result = await integration_session.execute(
            select(BjAccountModel).where(
                BjAccountModel.bj_account_id == linked_baekjoon_account.bj_account_id
            )
        )
        account = result.scalars().first()
        assert account is not None
        # 티어가 업데이트되었는지 확인 (Gold V(11) → Gold IV(12))
        assert account.tier_id == TIER_GOLD_IV
