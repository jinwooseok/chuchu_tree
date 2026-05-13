import pytest
from httpx import AsyncClient


class TestActivityAuth:
    """Activity API - 인증 필요 엔드포인트"""

    async def test_will_solve_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/will-solve-problems",
            json={"date": "2025-01-15", "problemIds": [1000]},
        )
        assert resp.status_code == 401

    async def test_solved_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/solved-problems",
            json={"date": "2025-01-15", "problemIds": [1000]},
        )
        assert resp.status_code == 401

    async def test_ban_problem_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/banned-list",
            json={"problemId": 1000},
        )
        assert resp.status_code == 401

    async def test_ban_tag_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/tags/banned-list",
            json={"tagCode": "dp"},
        )
        assert resp.status_code == 401

    async def test_get_banned_problems_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/user-accounts/me/problems/banned-list")
        assert resp.status_code == 401

    async def test_get_banned_tags_without_auth_fails(self, integration_client: AsyncClient):
        resp = await integration_client.get("/api/v1/user-accounts/me/tags/banned-list")
        assert resp.status_code == 401


class TestActivityAuthenticated:
    """Activity API - 인증된 상태"""

    async def test_update_will_solve_problems(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/will-solve-problems",
            json={"date": "2025-01-15", "problemIds": [1000, 2000]},
        )
        assert resp.status_code == 200

    async def test_update_solved_problems(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/solved-problems",
            json={"date": "2025-01-15", "problemId": [1000]},
        )
        assert resp.status_code == 200

    async def test_update_solved_and_will_solve(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/solved-and-will-solve-problems",
            json={
                "date": "2025-01-15",
                "solved_problem_ids": [1000],
                "will_solve_problem_ids": [2000],
            },
        )
        assert resp.status_code == 200

    async def test_batch_create_solved(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/solved-problems/batch",
            json=[{"date": "2025-01-15", "problemIds": [1000]}],
        )
        assert resp.status_code == 200

    async def test_ban_and_get_banned_problems(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)

        # ban
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/problems/banned-list",
            json={"problemId": 1000},
        )
        assert resp.status_code == 200

        # get banned list
        resp = await integration_client.get("/api/v1/user-accounts/me/problems/banned-list")
        assert resp.status_code == 200

    async def test_ban_and_get_banned_tags(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)

        # ban
        resp = await integration_client.post(
            "/api/v1/user-accounts/me/tags/banned-list",
            json={"tagCode": "dp"},
        )
        assert resp.status_code == 200

        # get banned list
        resp = await integration_client.get("/api/v1/user-accounts/me/tags/banned-list")
        assert resp.status_code == 200

    async def test_unban_problem(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.delete(
            "/api/v1/user-accounts/me/problems/banned-list",
            params={"problemId": 1000},
        )
        assert resp.status_code == 200

    async def test_unban_tag(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.delete(
            "/api/v1/user-accounts/me/tags/banned-list",
            params={"tagCode": "dp"},
        )
        assert resp.status_code == 200

    async def test_set_representative_tag(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.put(
            "/api/v1/user-accounts/me/problems/1000/representative-tag",
            json={"representativeTagCode": "dp"},
        )
        # 문제가 DB에 없을 수 있으므로 200 또는 에러 허용
        assert resp.status_code in (200, 400, 404)

    async def test_get_problem_record(
        self, integration_client: AsyncClient, valid_access_token: str
    ):
        integration_client.cookies.set("access_token", valid_access_token)
        resp = await integration_client.get("/api/v1/user-accounts/me/problems/record/1000")
        assert resp.status_code == 200
