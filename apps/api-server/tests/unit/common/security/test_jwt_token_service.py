import pytest
from datetime import timedelta

from app.common.infra.security.jwt_token_service import JwtTokenService
from app.core.exception import APIException


class TestJwtTokenServiceCreateRefreshToken:
    """JwtTokenService.create_refresh_token() 테스트"""

    def _make_service(self) -> JwtTokenService:
        return JwtTokenService(
            secret_key="test-secret-key-for-unit-tests",
            algorithm="HS256"
        )

    def test_create_refresh_token_returns_tuple(self):
        service = self._make_service()

        result = service.create_refresh_token(
            payload={"user_account_id": 42},
            expires_delta=timedelta(days=7)
        )

        assert isinstance(result, tuple)
        assert len(result) == 2
        token, jti = result
        assert isinstance(token, str)
        assert isinstance(jti, str)
        assert len(jti) == 36  # UUID4 형식

    def test_create_refresh_token_contains_jti_and_type(self):
        service = self._make_service()

        token, jti = service.create_refresh_token(
            payload={"user_account_id": 42},
            expires_delta=timedelta(days=7)
        )

        # 토큰 디코딩 후 jti와 type 필드 확인
        decoded = service.decode_token(token)
        assert decoded["jti"] == jti
        assert decoded["type"] == "refresh"
        assert decoded["user_account_id"] == 42

    def test_create_refresh_token_unique_jti(self):
        service = self._make_service()

        _, jti1 = service.create_refresh_token(
            payload={"user_account_id": 42},
            expires_delta=timedelta(days=7)
        )
        _, jti2 = service.create_refresh_token(
            payload={"user_account_id": 42},
            expires_delta=timedelta(days=7)
        )

        assert jti1 != jti2

    def test_create_refresh_token_expired_raises(self):
        service = self._make_service()

        token, _ = service.create_refresh_token(
            payload={"user_account_id": 42},
            expires_delta=timedelta(seconds=-1)
        )

        with pytest.raises(APIException) as exc_info:
            service.decode_token(token)

        assert exc_info.value.error_code == "EXPIRED_TOKEN"


class TestJwtTokenServiceCreateToken:
    """JwtTokenService.create_token() 기존 기능 회귀 테스트"""

    def _make_service(self) -> JwtTokenService:
        return JwtTokenService(
            secret_key="test-secret-key-for-unit-tests",
            algorithm="HS256"
        )

    def test_create_token_and_decode(self):
        service = self._make_service()

        token = service.create_token(
            payload={"user_account_id": 42},
            expires_delta=timedelta(hours=6)
        )

        decoded = service.decode_token(token)
        assert decoded["user_account_id"] == 42

    def test_create_token_does_not_have_jti(self):
        service = self._make_service()

        token = service.create_token(
            payload={"user_account_id": 42},
            expires_delta=timedelta(hours=6)
        )

        decoded = service.decode_token(token)
        assert "jti" not in decoded

    def test_decode_invalid_token_raises(self):
        service = self._make_service()

        with pytest.raises(APIException) as exc_info:
            service.decode_token("invalid.token.here")

        assert exc_info.value.error_code == "INVALID_TOKEN"
